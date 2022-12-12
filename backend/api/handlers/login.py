import logging
import bcrypt
import jwt
import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
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
    user = await request.app.db_clients["mongo"].find(filter, coll="users")
    if not user:
        LOG.debug("user not found")
        return error_pages.get_error_page(request, RequestError.not_found)

    hashed_pw = user.get("hashed_pw", None)
    if not hashed_pw:
        return error_pages.get_error_page(request, RequestError.corrupt)

    if bcrypt.checkpw(password.encode(), hashed_pw):
        # update user session
        session = await get_session(request)

        user_data = {
            "user_id": str(user["_id"]),
            "user_name": user["name"],
            "is_admin": user.get("is_admin", False),
            "lores_owned": user.get("lores_owned", []),
            "lores_access": user.get("lores_access", []),
        }
        session.update({**user_data})  # "raw_cookie": raw_cookie})

        return aiohttp_jinja2.render_template("index.html", request, None)
    else:
        return error_pages.get_error_page(request, RequestError.failed_login)


async def get(request: web.Request) -> web.Response:
    return aiohttp_jinja2.render_template("login.html", request, None)
