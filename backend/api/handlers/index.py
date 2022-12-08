import aiohttp_jinja2
from aiohttp import web
from backend.api.middlewares import allow_unauth

@allow_unauth
async def index_handler(request: web.Request) -> web.Response:
    context = {}
    return aiohttp_jinja2.render_template("index.html", request, context)
