import os
import aiohttp_jinja2
from aiohttp import web
from . import context_processors


async def index_handler(request):
    context = {}
    return aiohttp_jinja2.render_template("index.html", request, context)


async def favicon_handler(request):
    path = os.path.join(request.app.base_path, "static", "favicon.ico")
    return web.FileResponse(path=path)


async def general_handler(request):
    article_type = request.match_info['article_type']
    context = await context_processors.get_render_context(request)
    if not context:
        # TODO 404 page
        return aiohttp_jinja2.render_template("index.html", request, context={}, status=404)

    return aiohttp_jinja2.render_template("{}.html".format(article_type), request, context)
