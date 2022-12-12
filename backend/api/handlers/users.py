import logging
import bcrypt
import jwt
import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from backend.api.handlers import error_pages
from backend.api.errors import RequestError
from backend.api.middlewares import allow_unauth

LOG = logging.getLogger(__name__)


async def get(request: web.Request) -> web.Response:
    # TODO admin func
    pass


@allow_unauth
async def post(request: web.Request) -> web.Response:
    data = await request.json()
    user_name = data["user_name"]
    password = data["password"]

    if not user_name or not password:
        return error_pages.get_error_page(request, RequestError.malformed_request)
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    user = {
        "name": user_name,
        "hashed_pw": hashed_pw,
        "lores_owned": [],
        "lores_access": [],
    }
    result = await request.app.db_clients["mongo"].store(user, coll="users")
    if not result:
        return RequestError.service_unavailable
    return {"data": result, "status": 200}


async def put(request: web.Request) -> web.Response:
    data = await request.json()
    user_id = request.match_info.get("user_id")
    if not user_id or not ObjectId.is_valid(user_id):
        return RequestError.not_found

    filter = {"_id": user_id}
    result = await request.app.db_clients["mongo"].update(filter, data)
    if not result:
        return RequestError.service_unavailable
    return {"data": result, "status": 200}


async def delete(request: web.Request) -> web.Response:
    # TODO admin only func
    pass
