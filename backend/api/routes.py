import logging
import os
import prometheus_async.aio
from aiohttp import web
from backend.api.handlers import favicon, index, records, users, login

LOG = logging.getLogger(__name__)


def register(app):
    routes = web.RouteTableDef()

    routes.get("/metrics")(prometheus_async.aio.web.server_stats)
    routes.get("/")(index.index_handler)
    routes.get("/favicon.ico")(favicon.favicon_handler)

    # records
    routes.get("/records/{identifier}")(records.get)
    routes.post("/records")(records.post)
    routes.put("/records/{record_id}")(records.put)
    routes.delete("/records/{record_id}")(records.delete)

    # users
    routes.get("/users/{identifier}")(users.get)
    routes.post("/users")(users.post)
    routes.post("/register")(users.post)
    routes.put("/users/{user_id}")(users.put)
    routes.delete("/users/{user_id}")(users.delete)

    # login
    routes.get("/login")(login.get)
    routes.post("/login")(login.post)

    app.router.add_static(
        "/static",
        path=os.path.join(app.base_path, "static"),
        name="static",
        append_version=True,
    )

    app.add_routes(routes)
