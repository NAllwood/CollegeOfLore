import logging
import os
import prometheus_async.aio
import functools
from aiohttp import web
from . import handlers


LOG = logging.getLogger(__name__)


def register(app):
    routes = web.RouteTableDef()

    routes.get('/metrics')(prometheus_async.aio.web.server_stats)
    routes.get('/')(handlers.index_handler)
    routes.get('/favicon.ico')(handlers.favicon_handler)
    routes.get('/{article_type}/{name}')(handlers.general_handler)

    app.router.add_static('/static',
                          path=os.path.join(
                              app.base_path, 'static'),
                          name='static',
                          append_version=True)

    app.add_routes(routes)
