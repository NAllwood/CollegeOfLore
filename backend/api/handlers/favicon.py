import os
from aiohttp import web
from backend.api.middlewares import allow_unauth

@allow_unauth
async def favicon_handler(request: web.Request) -> web.Response:
    path = os.path.join(request.app.base_path, "static", "favicon.ico")
    return web.FileResponse(path=path)
