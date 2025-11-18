from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import settings

from logging import getLogger

logger = getLogger()
logger.setLevel(settings.LOG_LEVEL)

db_client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None

async def init_db_client():
    global db_client, db
    logger.info(f"Connecting to Database")
    try:
        db_client = AsyncIOMotorClient(
            settings.MONGO_CONNECTION_STRING,
            maxPoolSize=100,
            minPoolSize=10,
            timeoutMS=5000
            )
        await db_client.admin.command('ping')
        
        db = db_client[settings.MONGO_DATABASE_NAME]
    
    except Exception as e:
        logger.error("Error connecting to database")
        logger.debug(e)
        raise e
    logger.info("Database connected")
    
    
    logger.info("Checking collections...")
    required_collections = ["accounts"]         # Collections to be used further.
    
    try:
        existing_collections = await db.list_collection_names()
        
        for collection_name in required_collections:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
                logger.info(f"Collection '{collection_name}' created.")
            else:
                logger.info(f"Collection '{collection_name}' already exists.")
    
    except Exception as e:
        logger.error(f"Error checking/creating collections: {e}")
        raise
        
    logger.info("Database client initialized and collections checked.")
    
def close_db_client():
    global db_client, db
    logger.info(f"Closing Database")
    try:
        db_client.close()
    except Exception as e:
        logger.error("Error closing database")
        logger.debug(e)