from ..db.TransfersRepository import TransfersRepository
from ..models.Transactions import TransactionCreate
from ..models.Transactions import TransactionBase
from ..models.Transactions import TransactionView
from ..core import extensions as ext
from ..core.config import settings
from logging import getLogger
import httpx

logger = getLogger(__name__)


class TransferService:
    def __init__(self, repository: TransfersRepository | None = None):
        self.repo = repository or TransfersRepository(ext.db)
        self.accounts_url = settings.ACCOUNTS_SERVICE_URL.rstrip("/")

    async def create_transaction(self, data: TransactionCreate) -> dict:
        if data.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if data.sender == data.receiver:
            raise ValueError("Sender and receiver must be different")

        tx = TransactionBase(
            sender=data.sender,
            receiver=data.receiver,
            quantity=data.quantity,
        )
        tx_doc = tx.model_dump(by_alias=True)
        inserted = await self.repo.insert_transaction(tx_doc)

        async with httpx.AsyncClient(timeout=10.0) as client:
            debit_url = f"{self.accounts_url}/v1/accounts/operation/{data.sender}"
            resp = await client.patch(debit_url, json={"balance": -int(data.quantity)})
            if resp.status_code == 403:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "insufficient_funds", "transaction": inserted}
            if resp.status_code == 404:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "sender_not_found", "transaction": inserted}
            if resp.status_code >= 400:
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "debit_error", "transaction": inserted}

            credit_url = f"{self.accounts_url}/v1/accounts/operation/{data.receiver}"
            resp2 = await client.patch(credit_url, json={"balance": int(data.quantity)})
            if resp2.status_code == 404:
                await client.patch(debit_url, json={"balance": int(data.quantity)})
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "receiver_not_found", "transaction": inserted}
            if resp2.status_code >= 400:
                await client.patch(debit_url, json={"balance": int(data.quantity)})
                await self.repo.update_transaction_status(inserted["id"], "failed")
                return {"status": "failed", "reason": "credit_error", "transaction": inserted}

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

        async with httpx.AsyncClient(timeout=10.0) as client:
            debit_url = f"{self.accounts_url}/v1/accounts/operation/{receiver}"
            resp = await client.patch(debit_url, json={"balance": -quantity})
            if resp.status_code == 403:
                return {"status": "failed", "reason": "receiver_insufficient_funds", "transaction": tx}
            if resp.status_code >= 400:
                return {"status": "failed", "reason": "debit_receiver_error", "transaction": tx}

            credit_url = f"{self.accounts_url}/v1/accounts/operation/{sender}"
            resp2 = await client.patch(credit_url, json={"balance": quantity})
            if resp2.status_code >= 400:
                await client.patch(debit_url, json={"balance": quantity})
                return {"status": "failed", "reason": "credit_sender_error", "transaction": tx}

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
