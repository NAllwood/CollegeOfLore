from backend.db_clients.base_client import DBClient
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
import logging


LOG = logging.getLogger(__name__)


class MigrationMongoClient(DBClient):
    """ Makes calling backend code for migrations easier because DBClient provided without needing an app
    """

    def __init__(self, db: AsyncIOMotorDatabase, default_coll="records"):
        self.default_coll = default_coll
        self.db = db

    async def store(self, data: dict, **kwargs) -> Optional[ObjectId]:
        collection = kwargs.get("coll", self.default_coll)
        result = await self.db[collection].insert_one(data)
        if result.acknowledged:
            return result.inserted_id
        return None

    async def find(self, *args, **kwargs) -> Optional[dict]:
        collection = kwargs.get("coll", self.default_coll)
        return await self.db[collection].find_one(*args, **kwargs)

    async def find_many(self, *args, **kwargs) -> list:
        collection = kwargs.get("coll", self.default_coll)
        records = []
        async for document in self.db[collection].find(*args, **kwargs):
            records.append(document)
        return records

    async def delete(self, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        result = await self.db[collection].delete_one(*args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def delete_many(self, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        result = await self.db[collection].delete_many(*args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def update(self, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        result = await self.db[collection].update_one(*args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None

    async def update_many(self, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        result = await self.db[collection].update_many(*args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None
