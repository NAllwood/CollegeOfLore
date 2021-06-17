import logging
import os
import aiohttp
import aiohttp_jinja2
import prometheus_async.aio
import yaml
from aiohttp import web


LOG = logging.getLogger(__name__)


def get_render_context(base_path: str, name: str) -> dict:
    if name is None:
        # TODO return error page
        return None

    try:
        yaml_path = os.path.join(
            base_path, "lore", "persons", "{}.yml".format(name))
        with open(yaml_path, "r") as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.Loader)
    except FileNotFoundError:
        print("yaml file missing for '{}'".format(yaml_path))
        return None


def get_static_url(static_file: str) -> str:
    return os.path.join('static/', static_file)


async def index_handler(request):
    context = {}
    context['static'] = request.app.static_url
    return aiohttp_jinja2.render_template("index.html", request, context)


async def person_handler(request):
    context = {}
    context['static'] = request.app.static_url

    specific_context = get_render_context(
        request.app['base_path'], request.match_info['name'])

    if not specific_context:
        return aiohttp_jinja2.render_template("index.html", request, context)

    context.update(**specific_context)
    return aiohttp_jinja2.render_template("person.html", request, context)


def register(app):
    app.static_url = get_static_url
    routes = web.RouteTableDef()
    routes.static(
        '/static', path=os.path.join(app['base_path'], 'static'), name='static', append_version=True)

    routes.get('/metrics')(prometheus_async.aio.web.server_stats)
    routes.get('/')(index_handler)
    routes.get('/person/{name}')(person_handler)
    app.add_routes(routes)
