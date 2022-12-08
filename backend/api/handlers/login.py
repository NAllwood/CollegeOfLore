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


@allow_unauth
async def post(request: web.Request) -> web.Response:
    data = await request.json()
    user_name = data["user_name"]
    password = data["password"]

    if not user_name or not password:
        return error_pages.get_error_page(request, RequestError.malformed_request)

    filter = {"name": user_name}
    user = await request.app.db_clients["default"].find(filter)
    if not user:
        return error_pages.get_error_page(request, RequestError.not_found)

    hashed_pw = user.get("hashed_pw", None)
    if not hashed_pw:
        return error_pages.get_error_page(request, RequestError.corrupt)

    if bcrypt.checkpw(password.encode(), hashed_pw):
        user_data = {
            "user_id": user["_id"],
            "user_name": user_name,
            "is_admin": user.get("is_admin", False),
        }
        raw_cookie = jwt.encode(
            user_data, request.app.config["cookie"]["secret"], algorithms=["HS256"]
        )
        request["session"].update({**user_data, "raw_cookie": raw_cookie})
        return aiohttp_jinja2.render_template("index.html", request, None)
    else:
        return error_pages.get_error_page(request, RequestError.failed_login)


async def get(request: web.Request) -> web.Response:
    return aiohttp_jinja2.render_template("login.html", request, None)
