from backend.db_clients.base_client import DBClient
from backend import mongo
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import Optional


class MongoClient(DBClient):
    """ Class wrapping motor asyncio client for abstactred database access.
        Instances take a single mongo connection specified in the config yml.
        Uses "records" as default collection.
    """

    def __init__(self, app: web.Application, mongo_name: str, default_coll="records"):
        """Initializes the MongoClient and appends it to the provided web Application for access.

        Args:
            mongo_name (str): name of the mongo connection (needs to be the same as in config!)
        """

        self.default_coll = default_coll
        conn_name = "mongo" if mongo_name == "default" else f"mongo_{mongo_name}"
        db_name = app.config["mongodb"][mongo_name]["db"]
        self.db = app[conn_name][db_name]
        app.db_clients[mongo_name] = self

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
