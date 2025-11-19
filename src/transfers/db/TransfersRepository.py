from logging import getLogger
from bson import ObjectId

logger = getLogger()


class TransfersRepository:
    def __init__(self, db):
        self.collection = db["transactions"]

    async def insert_transaction(self, data: dict) -> dict:
        # data should be a dict serializable to BSON
        result = await self.collection.insert_one(data)
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        if created_doc:
            created_doc["id"] = str(created_doc.pop("_id"))
        return created_doc

    async def find_transaction_by_id(self, id_str: str) -> dict | None:
        try:
            _id = ObjectId(id_str)
        except Exception:
            return None
        doc = await self.collection.find_one({"_id": _id})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def find_transactions_by_user(self, user_id: str) -> list:
        cursor = self.collection.find({"$or": [{"sender": user_id}, {"receiver": user_id}]})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    async def find_transactions_sent_by_user(self, user_id: str) -> list:
        cursor = self.collection.find({"sender": user_id})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    async def find_transactions_received_by_user(self, user_id: str) -> list:
        cursor = self.collection.find({"receiver": user_id})
        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    async def update_transaction_status(self, id_str: str, status: str) -> dict | None:
        try:
            _id = ObjectId(id_str)
        except Exception:
            return None
        await self.collection.update_one({"_id": _id}, {"$set": {"status": status}})
        return await self.find_transaction_by_id(id_str)
