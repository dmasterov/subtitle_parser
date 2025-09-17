from motor.motor_asyncio import AsyncIOMotorClient

class MongoClient:
    def __init__(self, config):
        uri = f"mongodb://{config.username}:{config.password}@{config.host}:{config.port}"
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[config.db_name]
        self.collection = self.db[config.collection_name]

    async def insert_sample(self, doc: dict):
        await self.collection.insert_one(doc)
    
    async def insert_many(self, docs: list):
        await self.collection.insert_many(docs)