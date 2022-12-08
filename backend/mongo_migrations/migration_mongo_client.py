import datetime
from backend.db_clients.base_client import DBClient
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
import logging


LOG = logging.getLogger(__name__)


class MigrationMongoClient(DBClient):
    """Makes calling backend code for migrations easier because DBClient provided without needing an app"""

    def __init__(self, db: AsyncIOMotorDatabase, default_coll="records"):
        self.default_coll = default_coll
        self.db = db

    async def store(self, data: dict, **kwargs) -> Optional[ObjectId]:
        collection = kwargs.get("coll", self.default_coll)
        data.update({"creation_date": datetime.datetime.utcnow()})
        result = await self.db[collection].insert_one(data)
        if result.acknowledged:
            return result.inserted_id
        return None

    async def find(self, filter, *args, **kwargs) -> Optional[dict]:
        collection = kwargs.get("coll", self.default_coll)
        return await self.db[collection].find_one(filter, *args, **kwargs)

    async def find_many(self, filter, *args, **kwargs) -> list:
        collection = kwargs.get("coll", self.default_coll)
        documents = []
        async for document in self.db[collection].find(filter, *args, **kwargs):
            documents.append(document)
        return documents

    async def delete(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        if kwargs.pop("false_delete", False):
            data.update({"deletion_date": datetime.datetime.utcnow()})
            return await self.update(filter, data, *args, **kwargs)

        result = await self.db[collection].delete_one(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def delete_many(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        if kwargs.pop("false_delete", False):
            data.update_many({"deletion_date": datetime.datetime.utcnow()})
            return await self.update(filter, data, *args, **kwargs)

        result = await self.db[collection].delete_many(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def update(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        data.update({"last_modified": datetime.datetime.utcnow()})
        result = await self.db[collection].update_one(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None

    async def update_many(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.get("coll", self.default_coll)
        data.update({"last_modified": datetime.datetime.utcnow()})
        result = await self.db[collection].update_many(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None
