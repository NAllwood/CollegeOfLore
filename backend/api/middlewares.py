import logging
import jwt
from aiohttp_session import get_session
from aiohttp import web
from asyncio import InvalidStateError
from bson.json_util import dumps
from .errors import RequestError
from .handlers import error_pages
from urllib.parse import urlparse

LOG = logging.getLogger(__name__)


def allow_unauth(func):
    func.allow_unauth = True
    return func


async def _get_user_session(request: web.Request) -> dict:
    app = request.app
    session = await get_session(request)

    required_fileds = ["user_id", "user_name", "lores_owned", "lores_access"]
    if not all([True if name in session.keys() else False for name in required_fileds]):
        return RequestError.not_authenticated

    return session


async def auth_middleware(_, handler):
    async def middleware_handler(request: web.Request):
        resource_name = None if "/" not in request.path else request.path.split("/")[1]

        # OPTIONS requests are directly answered by aiohttp_cors
        # no_auth_resources as /login or css+js should be available without auth
        if not getattr(handler, "allow_unauth", False) and resource_name != "static":
            session = await _get_user_session(request)
            if not session:
                LOG.error("Invalid Session: No session")
                return build_api_response(RequestError.not_authenticated)
            if "error" in session:
                return build_api_response(error_pages.get_error_page(request, session))
            request["session"] = session

        try:
            response = await handler(request)
        except InvalidStateError as e:
            LOG.exception("Invalid future state")
            return build_api_response(
                error_pages.get_error_page(request, RequestError.conflict)
            )

        return build_api_response(response)

    return middleware_handler


def build_api_response(response: dict):
    headers = {}

    # if not app_cfg['settings'].get('aiohttp_cors'):
    #     allowed_origin = app_cfg['settings']['allowed_origin']
    #     headers.update({
    #         'Access-Control-Allow-Origin': allowed_origin,
    #         'Access-Control-Allow-Credentials': 'true'
    #     })

    if isinstance(response, web.Response) or isinstance(response, web.FileResponse):
        return response

    if response is None:
        headers.update(
            {
                "Access-Control-Allow-Headers": "content-type",
                "Access-Control-Allow-Methods": "POST, GET, DELETE, PUT, OPTIONS",
            }
        )
        return web.Response(headers=headers)

    data = response.get("data", None)
    # let bson_util handle dumping the response data or aiohttp will complain that
    # bson ids are not json dumpable
    if data:
        data = dumps(data)

    status = response.get("status", 400)

    payload = {
        "data": data,
        "message": response.get("message", ""),
        "error": response.get("error", None),
    }
    # dumps = partial(json.dumps, default=map_from_bson)
    return web.json_response(payload, status=status, headers=headers)
