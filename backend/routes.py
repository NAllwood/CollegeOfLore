import logging
import os
import prometheus_async.aio
from aiohttp import web
from backend.handlers import favicon, index, records


LOG = logging.getLogger(__name__)


def register(app):
    routes = web.RouteTableDef()

    routes.get("/metrics")(prometheus_async.aio.web.server_stats)
    routes.get("/")(index.index_handler)
    routes.get("/favicon.ico")(favicon.favicon_handler)

    routes.get("/records/{identifier}")(records.get)
    routes.post("/records")(records.post)
    routes.put("/records/{record_id}")(records.put)
    routes.delete("/records/{record_id}")(records.delete)

    app.router.add_static(
        "/static",
        path=os.path.join(app.base_path, "static"),
        name="static",
        append_version=True,
    )

    app.add_routes(routes)
