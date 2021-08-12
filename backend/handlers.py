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
    context = await context_processors.get_record_context(request)
    if not context:
        # TODO prettier error page (design, multiple error messages from a collection)
        status = 404
        context = {"error_code": status, "error_msg": "File Not Found"}
        return aiohttp_jinja2.render_template(
            "error.html", request, context={}, status=status
        )

    record_type = context.get("type")
    if not record_type:
        # TODO prettier error page (design, multiple error messages from a collection)
        status = 500
        context = {
            "error_code": status,
            "error_msg": "The college has the scrolls you are looking for but sadly they are half burnt and barely readable.",
        }
        return aiohttp_jinja2.render_template(
            "error.html", request, context={}, status=status
        )

    return aiohttp_jinja2.render_template(
        "{}.html".format(record_type), request, context
    )
