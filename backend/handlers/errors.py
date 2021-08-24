import aiohttp_jinja2
from aiohttp import web


def get_404_page(request: web.Request) -> web.Response:
    # TODO prettier error page (design, multiple error messages from a collection)
    status = 404
    context = {"error_code": status, "error_msg": "File Not Found"}
    return aiohttp_jinja2.render_template(
        "error.html", request, context=context, status=status
    )


def get_500_page(request: web.Request) -> web.Response:
    # TODO prettier error page (design, multiple error messages from a collection)
    status = 500
    context = {
        "error_code": status,
        "error_msg": "The college has the scrolls you are looking for but sadly they are half burnt and barely readable.",
    }
    return aiohttp_jinja2.render_template(
        "error.html", request, context=context, status=status
    )
