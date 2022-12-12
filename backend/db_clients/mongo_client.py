import datetime
from backend.db_clients.base_client import DBClient
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import Optional


class MongoClient(DBClient):
    """Class wrapping motor asyncio client for abstracted database access.
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
        app.db_clients[conn_name] = self

    async def store(self, data: dict, **kwargs) -> Optional[ObjectId]:
        collection = kwargs.pop("coll", self.default_coll)
        data.update({"creation_date": datetime.datetime.utcnow()})
        result = await self.db[collection].insert_one(data)
        if result.acknowledged:
            return result.inserted_id
        return None

    async def find(self, filter, *args, **kwargs) -> Optional[dict]:
        collection = kwargs.pop("coll", self.default_coll)
        return await self.db[collection].find_one(filter, *args, **kwargs)

    async def find_many(self, filter, *args, **kwargs) -> list:
        collection = kwargs.pop("coll", self.default_coll)
        documents = []
        async for document in self.db[collection].find(filter, *args, **kwargs):
            documents.append(document)
        return documents

    async def delete(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.pop("coll", self.default_coll)
        if kwargs.pop("false_delete", False):
            data.update({"deletion_date": datetime.datetime.utcnow()})
            return await self.update(filter, data, *args, **kwargs)

        result = await self.db[collection].delete_one(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def delete_many(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.pop("coll", self.default_coll)
        if kwargs.pop("false_delete", False):
            data.update_many({"deletion_date": datetime.datetime.utcnow()})
            return await self.update(filter, data, *args, **kwargs)

        result = await self.db[collection].delete_many(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.deleted_count
        return None

    async def update(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.pop("coll", self.default_coll)
        data.update({"last_modified": datetime.datetime.utcnow()})
        result = await self.db[collection].update_one(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None

    async def update_many(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.pop("coll", self.default_coll)
        data.update({"last_modified": datetime.datetime.utcnow()})
        result = await self.db[collection].update_many(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None

    async def replace(self, filter, data, *args, **kwargs) -> Optional[int]:
        collection = kwargs.pop("coll", self.default_coll)
        data.update({"last_modified": datetime.datetime.utcnow()})
        result = await self.db[collection].replace_one(filter, data, *args, **kwargs)
        if result.acknowledged:
            return result.modified_count
        return None
