from logging import getLogger
from datetime import datetime, timezone
import httpx
from aiobreaker import CircuitBreakerError

from ..core.config import settings
from ..clients.ServiceClient import ServiceClient
from ..models.Transactions import TransactionCreate, TransactionBase
from ..db.TransfersRepository import TransfersRepository
from ..db.RedisCachedTransfersRepository import RedisCachedTransfersRepository

logger = getLogger(__name__)

from ..core import extensions

class TransferService:
    def __init__(self, redis_client=None, repository=None, client=None, jwt=None):
        if repository:
            self.repo = repository
        elif redis_client:
            self.repo = RedisCachedTransfersRepository(extensions.db, redis_client)
        else:
            self.repo = TransfersRepository(extensions.db)
            
        self.client = client or ServiceClient(settings.ACCOUNTS_SERVICE_URL, jwt=jwt)
        self.redis_client = redis_client
        self.jwt = jwt

    async def create_transaction(self, data: TransactionCreate) -> dict:
        if data.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if data.sender == data.receiver:
            raise ValueError("Sender and receiver must be different")

        sender_balance = None
        receiver_balance = None
        sender_subscription = None
        
        try:
            sender_resp = await self.client.get_account(data.sender)
            logger.info(f"Sender account resp: {sender_resp.status_code} - {sender_resp.text}")
            if sender_resp.status_code == 200:
                sender_data = sender_resp.json()
                sender_balance = sender_data.get("balance")
                sender_subscription = sender_data.get("subscription")
                logger.info(f"Sender subscription: {sender_subscription}")
                logger.info(f"Sender balance: {sender_balance}")
                
            receiver_resp = await self.client.get_account(data.receiver)
            logger.info(f"Receiver account resp: {receiver_resp.status_code} - {receiver_resp.text}")
            if receiver_resp.status_code == 200:
                receiver_balance = receiver_resp.json().get("balance")
        except Exception as e:
            logger.error(f"Error fetching account details: {e}")

        # Validar límites de suscripción
        if sender_subscription:
            try:
                sent_resp = await self.client.get_sent_transactions(data.sender)
                if sent_resp.status_code == 200:
                    transactions = sent_resp.json()
                    logger.info(f"Fetched {len(transactions)} sent transactions for {data.sender}")
                    
                    # Filtrar transacciones completadas del mes actual
                    current_month = datetime.now(timezone.utc).month
                    current_year = datetime.now(timezone.utc).year
                    
                    completed_this_month = 0
                    for tx in transactions:
                        if tx.get("status") == "completed":
                            date_str = tx.get("date") or tx.get("gmt_time")
                            if date_str:
                                try:
                                    tx_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                    if tx_date.month == current_month and tx_date.year == current_year:
                                        completed_this_month += 1
                                except:
                                    pass
                    
                    # Verificar límites según suscripción
                    subscription_limits = {
                        "basico": 5,
                        "estudiante": 10,
                        "pro": float('inf')  # Ilimitadas
                    }
                    
                    limit = subscription_limits.get(sender_subscription, 0)
                    logger.info(f"Subscription: {sender_subscription}, Completed this month: {completed_this_month}, Limit: {limit}")
                    
                    if completed_this_month >= limit:
                        raise ValueError(f"Monthly transaction limit reached for {sender_subscription} subscription")
                        
            except ValueError:
                raise
            except Exception as e:
                logger.warning(f"Error checking transaction limits: {e}")

        # Verificar fraude antes de procesar la transacción (no bloqueante si el servicio no responde)
        try:
            fraud_resp = await self.client.get_fraud_check(data.sender, data.receiver, data.quantity)
            logger.info(f"Fraud check response: {fraud_resp.status_code} - {fraud_resp.text}")
            
            if fraud_resp.status_code == 200:
                fraud_data = fraud_resp.json()
                if fraud_data.get("message") != "No risk detected":
                    raise ValueError(f"Transaction rejected by fraud check: {fraud_data.get('message', 'Unknown reason')}")
            else:
                logger.warning(f"Fraud service returned non-200 status (non-blocking): {fraud_resp.status_code}")
        except ValueError:
            raise
        except Exception as e:
            logger.warning(f"Failed to check fraud service (non-blocking): {e}")

        # Obtener fecha GMT de API externa
        gmt_time = await self.client.get_gmt_time()
        if gmt_time:
            # Convertir el string ISO a datetime
            try:
                transaction_date = datetime.fromisoformat(gmt_time.replace('Z', '+00:00'))
                gmt_time = transaction_date.isoformat()
            except:
                transaction_date = datetime.now(timezone.utc)
        else:
            # Fallback a hora local UTC si falla la API
            transaction_date = datetime.now(timezone.utc)

        tx = TransactionBase(
            sender=data.sender,
            receiver=data.receiver,
            quantity=data.quantity,
            sender_balance=sender_balance,
            receiver_balance=receiver_balance,
            gmt_time=gmt_time,
            date=transaction_date
        )
        tx_doc = tx.model_dump(by_alias=True)
        inserted = await self.repo.insert_transaction(tx_doc)

        try:
            resp = await self.client.debit_account(data.sender, data.quantity)
            
            if resp.status_code == 403:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "insufficient_funds", "transaction": inserted}
            if resp.status_code == 404:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "sender_not_found", "transaction": inserted}
            if resp.status_code >= 400:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "debit_error", "transaction": inserted}

            resp2 = await self.client.credit_account(data.receiver, data.quantity)
            
            if resp2.status_code == 404:
                await self.client.credit_account(data.sender, data.quantity)
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "receiver_not_found", "transaction": inserted}
            if resp2.status_code >= 400:
                await self.client.credit_account(data.sender, data.quantity)
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "credit_error", "transaction": inserted}

        except CircuitBreakerError:
            logger.warning("Circuit Breaker Open: Skipping transaction creation")
            await self.repo.update_transaction_status(inserted["id"], "failed")
            return {"status": "failed", "reason": "service_unavailable", "transaction": inserted}
        except (httpx.RequestError, TimeoutError) as e:
            logger.error(f"Connection failed: {e}")
            await self.repo.update_transaction_status(inserted["id"], "failed")
            return {"status": "failed", "reason": "connection_error", "transaction": inserted}

        updated = await self.repo.update_transaction_status(inserted["id"], "completed")
        
        # Notificar al servicio de notificaciones (no bloquea la transacción si falla)
        try:
            notification_payload = {
                "type": "transaction",
                "userId": data.sender,
                "metadata": {
                    "amount": data.quantity,
                    "recipient": data.receiver
                }
            }
            headers = {"Content-Type": "application/json"}
            if self.jwt:
                headers["Authorization"] = self.jwt
            
            async with httpx.AsyncClient(timeout=10.0) as notification_client:
                notification_resp = await notification_client.post(
                    "http://localhost:10000/v1/notifications/events",
                    json=notification_payload,
                    headers=headers
                )
                logger.info(f"Notification sent: {notification_resp.status_code}")
        except Exception as e:
            logger.warning(f"Failed to send notification (non-blocking): {e}")
        
        return {"status": "completed", "transaction": updated}

    async def get_transaction(self, id_str: str) -> dict | None:
        return await self.repo.find_transaction_by_id(id_str)

    async def get_transactions_by_user(self, user_id: str) -> list:
        return await self.repo.find_transactions_by_user(user_id)

    async def get_transactions_sent_by_user(self, user_id: str) -> list:
        return await self.repo.find_transactions_sent_by_user(user_id)

    async def get_transactions_received_by_user(self, user_id: str) -> list:
        return await self.repo.find_transactions_received_by_user(user_id)

    async def revert_transaction(self, id_str: str) -> dict | None:
        tx = await self.repo.find_transaction_by_id(id_str)
        if not tx:
            return None
        if tx.get("status") != "completed":
            return {"status": "not_reverted", "reason": "transaction_not_completed", "transaction": tx}

        sender = tx.get("sender")
        receiver = tx.get("receiver")
        quantity = tx.get("quantity")

        try:
            resp = await self.client.debit_account(receiver, quantity)
            
            if resp.status_code == 403:
                return {"status": "failed", "reason": "receiver_insufficient_funds", "transaction": tx}
            if resp.status_code >= 400:
                return {"status": "failed", "reason": "debit_receiver_error", "transaction": tx}

            resp2 = await self.client.credit_account(sender, quantity)
            
            if resp2.status_code >= 400:
                await self.client.credit_account(receiver, quantity)
                return {"status": "failed", "reason": "credit_sender_error", "transaction": tx}
        
        except CircuitBreakerError:
            logger.warning("Circuit Breaker Open: Skipping transaction reversion")
            return {"status": "failed", "reason": "service_unavailable", "transaction": tx}
        except (httpx.RequestError, TimeoutError) as e:
            logger.error(f"Connection failed during revert: {e}")
            return {"status": "failed", "reason": "connection_error", "transaction": tx}

        updated = await self.repo.update_transaction_status(id_str, "reverted")
        return {"status": "reverted", "transaction": updated}

    async def delete_transaction(self, id_str: str) -> dict | None:
        tx = await self.repo.find_transaction_by_id(id_str)
        if not tx:
            return None

        if tx.get("status") == "completed":
            revert_res = await self.revert_transaction(id_str)
            if not isinstance(revert_res, dict) or revert_res.get("status") != "reverted":
                return revert_res

        deleted = await self.repo.delete_transaction(id_str)
        if not deleted:
            return {"status": "failed", "reason": "delete_failed", "transaction": tx}

        return {"status": "deleted", "transaction": deleted}

    async def update_status(self, id_str: str, new_status: str) -> dict | None:
        tx = await self.repo.find_transaction_by_id(id_str)
        if not tx:
            return None

        current = tx.get("status")
        if current is None:
            current = "pending"

        new_status = str(new_status)

        allowed_transitions = {
            "pending": {"completed", "failed"},
            "failed": {"completed", "pending"},
            "completed": {"reverted"},
            "reverted": set(),
        }

        allowed = allowed_transitions.get(current, {"completed", "failed", "reverted"})

        if new_status not in allowed:
            return {"status": "failed", "reason": "invalid_transition", "from": current, "to": new_status}

        updated = await self.repo.update_transaction_status(id_str, new_status)
        return {"status": "updated", "transaction": updated}


