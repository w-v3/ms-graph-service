import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.db.connection.base import IConnectionManager

logger = logging.getLogger(__name__)


class MongoConnectionManager(IConnectionManager):
    def __init__(self, uri: str, db_name: str):
        logger.info(f"connecting at {uri}")
        self.uri = uri
        self.db_name = db_name
        self.client = None

    async def connect(self):
        logger.info("Connecting to MongoDB , checking for pre-existing client")
        logger.info(f"connecting at {self.uri}")
        try:
            if self.client is None:
                self.client = AsyncIOMotorClient(self.uri)
            logger.info("Connected to MongoDB")

            return self.client[self.db_name]
        except:
            raise Exception

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    async def ensure_database(self):
        try:
            db = await self.connect()
            names = await db.list_collection_names()
            if self.db_name not in names:
                await db.create_collection(self.db_name)
                logger.info(f"Created {self.db_name} collection")
        except PyMongoError as e:
            logger.error(f"ensure_database failed: {e}")
            raise
