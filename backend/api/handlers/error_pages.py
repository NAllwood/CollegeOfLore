import aiohttp_jinja2
from aiohttp import web
from backend.api.errors import RequestError

"""Functions rendering error pages that can be returned by other handlers in case of an error"""

error_msg_switch = {
    400: "You seem to be speaking a dialect of some exotic language, that our scribes sadly cannot understand. Maybe you can try again in Common or Elvish?",
    401: "Maybe we can help you find the scrolls you seek, but first let me ask: Who are you?",
    403: "The knowledge you seek is forbidden!",
    404: "Sadly, we do not have the scrolls you seek. Maybe if you stumble upon them during your travels, you can donate them to the college?",
    410: "The college has the scrolls you are looking for but sadly they are half burnt and barely readable. We will dispose of them as soon as possible.",
    500: "When trying to fetch the Lore you requested, one of our students actually managed to collapse the whole corridor! We will try to get him out of there and bring you your scrolls as soon as possible. Maybe you'll find other stories interesting in the meantime?",
    503: "The college is currently closed for maintenance. We will open up again shortly"
}


def get_error_page(request: web.Request, error: RequestError) -> web.Response:
    # TODO prettier error page (design, multiple error messages from a collection)
    status = error["status"]
    context = {"error_code": status,
               "error": error["error"], "error_msg": error_msg_switch.get(status, "Something very unexpected happened.")}
    return aiohttp_jinja2.render_template(
        "error.html", request, context=context, status=status
    )
