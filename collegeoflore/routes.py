import logging
import os
import typing
import aiohttp_jinja2
import prometheus_async.aio
import yaml
import functools
from aiohttp import web


LOG = logging.getLogger(__name__)


def get_local_context(base_path: str, article_type: str, name: str) -> typing.Optional[dict]:
    """Creates path from parameters and attempts to locally find the corresponding. '.yml' file.

    Args:
        base_path (str): base path of the filesystem
        article_type (str): type of article to be loaded (person/place/item...)
        name (str): name of the article

    Returns:
        dict/None: the parsed dict, or None, if the yml was not found.
    """

    if name is None or article_type is None:
        # TODO return error page
        return None

    try:
        yaml_path = os.path.join(
            base_path, "lore", "{}".format(article_type), "{}.yml".format(name))
        with open(yaml_path, "r") as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.Loader)
    except FileNotFoundError:
        LOG.warning("yaml file missing for '{}'".format(yaml_path))
        return None


def get_render_context(base_path: str, article_type: str, name: str) -> typing.Optional[dict]:
    """Gets the specific information required to render an article page.

    Args:
        base_path (str): base path of the filesystem
        article_type (str): type of article to be loaded (person/place/item...)
        name (str): name of the article

    Returns:
        dict/None: a dict containing the article information, or None
    """

    # TODO USE MONGODB FOR INFO STORAGE LATER
    return get_local_context(base_path, article_type, name)


async def index_handler(request):
    context = {}
    context['static'] = request.app.static_url
    context['translate'] = request.app['translate']
    return aiohttp_jinja2.render_template("index.html", request, context)


async def favicon_handler(request):
    path = os.path.join(request.app["base_path"], "static", "favicon.ico")
    return web.FileResponse(path=path)


# async def person_handler(request):
#     context = {}
#     context['static'] = request.app.static_url
#     context['lang'] = request.app.lang
#     context['translate'] = request.app.translate

#     specific_context = get_render_context(
#         request.app['base_path'], request.match_info['name'])

#     if not specific_context:
#         # TODO 404
#         return aiohttp_jinja2.render_template("index.html", request, context)

#     context.update(**specific_context)
#     return aiohttp_jinja2.render_template("person.html", request, context)


async def general_handler(request):
    context = {}
    context['static'] = request.app.static_url
    context['translate'] = request.app['translate']

    article_type = request.match_info['article_type']

    specific_context = get_render_context(
        request.app['base_path'], article_type, request.match_info['name'])

    if not specific_context:
        LOG.warning("could not find specific rendering context")
        # TODO 404
        return aiohttp_jinja2.render_template("index.html", request, context)

    context.update(**specific_context)
    return aiohttp_jinja2.render_template("{}.html".format(article_type), request, context)


def wrap_static(func, static_file):
    '''wraps the applications static resource lookup function to call it with
       the parameter as keyword.'''
    return func(filename=static_file)


def setup_static_routes(app):
    resource = app.router.add_static('/static',
                                     path=os.path.join(
                                         app['base_path'], 'static'),
                                     name='static',
                                     append_version=True)
    app.static_url = functools.partial(wrap_static, resource.url_for)


def register(app):
    routes = web.RouteTableDef()

    routes.get('/metrics')(prometheus_async.aio.web.server_stats)
    routes.get('/')(index_handler)
    routes.get('/favicon.ico')(favicon_handler)
    # routes.get('/person/{name}')(person_handler)
    routes.get('/{article_type}/{name}')(general_handler)
    app.add_routes(routes)

    setup_static_routes(app)
