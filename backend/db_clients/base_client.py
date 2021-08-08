from abc import ABC
from typing import Optional
from aiohttp import web
from bson import ObjectId


class DBClient(ABC):
    """Abstract parent class for all data clients. Provides basic CRUD functions
    """

    def __init__(self, app: web.Application):
        pass

    async def store(self, data: dict, **kwargs) -> Optional[ObjectId]:
        pass

    async def find(self, *args, **kwargs) -> Optional[dict]:
        pass

    async def find_many(self, *args, **kwargs) -> list:
        pass

    async def delete(self, *args, **kwargs) -> Optional[int]:
        pass

    async def delete_many(self, *args, **kwargs) -> Optional[int]:
        pass

    async def update(self, *args, **kwargs) -> Optional[int]:
        pass

    async def update_many(self, *args, **kwargs) -> Optional[int]:
        pass
