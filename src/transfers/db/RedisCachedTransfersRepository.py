from logging import getLogger
import json
import redis.asyncio as redis
from .TransfersRepository import TransfersRepository

logger = getLogger()


class RedisCachedTransfersRepository(TransfersRepository):
    def __init__(self, db, redis_client: redis.Redis, ttl_seconds: int = 3600):
        super().__init__(db)
        self.redis = redis_client
        self.ttl = ttl_seconds

    def _get_transaction_key(self, id_str: str) -> str:
        return f"transaction:{id_str}"

    def _get_user_transactions_key(self, user_id: str) -> str:
        return f"user_transactions:{user_id}"

    async def find_transaction_by_id(self, id_str: str) -> dict | None:
        key = self._get_transaction_key(id_str)
        
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                try:
                    logger.info(f"Cache HIT (Redis): transaction = {id_str}")
                    return json.loads(cached_data)
                except Exception as e:
                    logger.error(f"Error deserializing cache for {id_str}: {e}")
        except redis.RedisError as e:
            logger.error(f"Redis error reading transaction {id_str}: {e}")

        transaction = await super().find_transaction_by_id(id_str)
        
        if transaction:
            try:
                await self.redis.set(key, json.dumps(transaction, default=str), ex=self.ttl)
                logger.info(f"Cache MISS: transaction cached in Redis: id = {id_str}")
            except redis.RedisError as e:
                logger.error(f"Redis error caching transaction {id_str}: {e}")
        
        return transaction

    async def find_transactions_by_user(self, user_id: str) -> list:
        key = self._get_user_transactions_key(user_id)
        
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                try:
                    logger.info(f"Cache HIT (Redis): user_transactions = {user_id}")
                    return json.loads(cached_data)
                except Exception as e:
                    logger.error(f"Error deserializing cache for user {user_id}: {e}")
        except redis.RedisError as e:
            logger.error(f"Redis error reading user transactions {user_id}: {e}")

        transactions = await super().find_transactions_by_user(user_id)
        
        if transactions:
            try:
                await self.redis.set(key, json.dumps(transactions, default=str), ex=self.ttl)
                logger.info(f"Cache MISS: user_transactions cached in Redis: user = {user_id}")
            except redis.RedisError as e:
                logger.error(f"Redis error caching user transactions {user_id}: {e}")
        
        return transactions

    async def insert_transaction(self, data: dict) -> dict:
        result = await super().insert_transaction(data)
        if result:
            sender = result.get("sender")
            receiver = result.get("receiver")
            if sender:
                await self._invalidate_user_cache(sender)
            if receiver:
                await self._invalidate_user_cache(receiver)
        return result

    async def update_transaction_status(self, id_str: str, status: str) -> dict | None:
        result = await super().update_transaction_status(id_str, status)
        if result:
            await self._invalidate_transaction_cache(id_str)
            sender = result.get("sender")
            receiver = result.get("receiver")
            if sender:
                await self._invalidate_user_cache(sender)
            if receiver:
                await self._invalidate_user_cache(receiver)
        return result

    async def delete_transaction(self, id_str: str) -> dict | None:
        result = await super().delete_transaction(id_str)
        if result:
            await self._invalidate_transaction_cache(id_str)
            sender = result.get("sender")
            receiver = result.get("receiver")
            if sender:
                await self._invalidate_user_cache(sender)
            if receiver:
                await self._invalidate_user_cache(receiver)
        return result

    async def _invalidate_transaction_cache(self, id_str: str):
        key = self._get_transaction_key(id_str)
        try:
            await self.redis.delete(key)
            logger.info(f"Cache key deleted: {key}")
        except redis.RedisError as e:
            logger.error(f"Redis error deleting key {key}: {e}")

    async def _invalidate_user_cache(self, user_id: str):
        key = self._get_user_transactions_key(user_id)
        try:
            await self.redis.delete(key)
            logger.info(f"Cache key deleted: {key}")
        except redis.RedisError as e:
            logger.error(f"Redis error deleting key {key}: {e}")
