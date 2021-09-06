import logging
import jwt
from aiohttp_session import get_session
from aiohttp import web
from asyncio import InvalidStateError
from .errors import RequestError
from .handlers import error_pages

LOG = logging.getLogger(__name__)


async def _get_user_session(request: web.Request) -> dict:
    app = request.app
    session = await get_session(request)
    if "is_admin" in session:
        return session

    if app.config["settings"].get("permit_all"):
        session['is_admin'] = True
        # TODO make this client IP/MAC at least
        session['user_id'] = "0"
        session['user_name'] = "SUPERUSER"
        return session

    # no token present (anymore)
    if not request.cookies.get('authtoken'):
        LOG.error('No auth cookie set')
        return RequestError.no_cookie

    # reset session because token has changed
    if session.get('raw_token') != request.cookies['authtoken']:
        cookie = jwt.decode(request.cookies['authtoken'],
                            app.config['cookie']['secret'],
                            algorithms=['HS256'])

        # TODO enforce expiration check
        exp = cookie.get('exp')
        if not exp:
            return RequestError.expired_cookie

        user = cookie.get('user', {})
        user_id = user.get('id')
        user_name = user.get('name')
        is_admin = cookie.get('is_admin', False)

        session['raw_token'] = request.cookies['authtoken']
        session["user_id"] = user_id
        session['is_admin'] = is_admin
        session['user_name'] = user_name

        if not user_id and not is_admin:
            return None

    return session


async def auth_middleware(_, handler):
    async def middleware_handler(request: web.Request):
        cookie = request.cookies.get('authtoken', None)
        unauth_options = request.method == "OPTIONS" and cookie is None

        if unauth_options:
            LOG.info("Answering OPTIONS request without requiring authentication")
            # Options requests are directly answered by aiohttp_cors
            return await build_api_response(handler(request))

        try:
            session = await _get_user_session(request)
        except jwt.exceptions.ExpiredSignatureError:
            LOG.error('Invalid Token: Expired Signature')
            return build_api_response(RequestError.expired_signature)
        except jwt.exceptions.InvalidSignatureError:
            LOG.error('Invalid Token: Invalid Signature')
            return build_api_response(RequestError.invalid_signature)
        except jwt.exceptions.DecodeError:
            LOG.error('Invalid Token: Decode Error')
            return build_api_response(RequestError.invalid_token)
        if not session:
            LOG.error('Invalid Token: No session')
            return build_api_response(RequestError.invalid_token)
        if "error" in session:
            return build_api_response(error_pages.get_error_page(request, session))

        request['session'] = session
        try:
            response = await handler(request)
        except InvalidStateError as e:
            LOG.exception('Invalid future state')
            return build_api_response(error_pages.get_error_page(request, RequestError.conflict))

        # only store permissions in session as long as the backend handles the
        # request. we dont want to overflow the response header
        if session.get('permissions'):
            del session['permissions']
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
        headers.update({
            'Access-Control-Allow-Headers': 'content-type',
            'Access-Control-Allow-Methods': 'POST, GET, DELETE, PUT, OPTIONS'
        })
        return web.Response(headers=headers)

    data = response.get('data', None)
    status = response.get('status', 400)

    payload = {
        'data': data,
        'message': response.get('message', ''),
        'error': response.get('error', None)
    }
    # dumps = partial(json.dumps, default=map_from_bson)
    return web.json_response(
        payload, status=status, headers=headers)
