from logging import getLogger
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
    def __init__(self, redis_client=None, repository=None, client=None):
        if repository:
            self.repo = repository
        elif redis_client:
            self.repo = RedisCachedTransfersRepository(extensions.db, redis_client)
        else:
            self.repo = TransfersRepository(extensions.db)
            
        self.client = client or ServiceClient(settings.ACCOUNTS_SERVICE_URL)
        self.redis_client = redis_client

    async def create_transaction(self, data: TransactionCreate) -> dict:
        if data.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if data.sender == data.receiver:
            raise ValueError("Sender and receiver must be different")

        sender_balance = None
        receiver_balance = None
        try:
            sender_resp = await self.client.get_account(data.sender)
            logger.info(f"Sender account resp: {sender_resp.status_code} - {sender_resp.text}")
            if sender_resp.status_code == 200:
                sender_balance = sender_resp.json().get("balance")
                
            receiver_resp = await self.client.get_account(data.receiver)
            logger.info(f"Receiver account resp: {receiver_resp.status_code} - {receiver_resp.text}")
            if receiver_resp.status_code == 200:
                receiver_balance = receiver_resp.json().get("balance")
        except Exception as e:
            logger.error(f"Error fetching account details: {e}")

        gmt_time = await self.client.get_gmt_time()

        tx = TransactionBase(
            sender=data.sender,
            receiver=data.receiver,
            quantity=data.quantity,
            sender_balance=sender_balance,
            receiver_balance=receiver_balance,
            gmt_time=gmt_time
        )
        tx_doc = tx.model_dump(by_alias=True)
        inserted = await self.repo.insert_transaction(tx_doc)

        try:
            resp = await self.client.debit_account(data.sender, int(data.quantity))
            
            if resp.status_code == 403:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "insufficient_funds", "transaction": inserted}
            if resp.status_code == 404:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "sender_not_found", "transaction": inserted}
            if resp.status_code >= 400:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "debit_error", "transaction": inserted}

            resp2 = await self.client.credit_account(data.receiver, int(data.quantity))
            
            if resp2.status_code == 404:
                await self.client.credit_account(data.sender, int(data.quantity))
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "receiver_not_found", "transaction": inserted}
            if resp2.status_code >= 400:
                await self.client.credit_account(data.sender, int(data.quantity))
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
        quantity = int(tx.get("quantity"))

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


