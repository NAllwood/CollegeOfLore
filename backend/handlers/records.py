import logging
import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from backend import context_processors
from backend import linker
from . import errors

LOG = logging.getLogger(__name__)


async def get(request: web.Request) -> web.Response:
    context = await context_processors.get_record_context(request)
    if not context:
        return errors.get_404_page(request)

    record_type = context.get("type")
    if not record_type:
        return errors.get_500_page(request)

    return aiohttp_jinja2.render_template(
        "{}.html".format(record_type), request, context
    )


async def post(request: web.Request) -> web.Response:
    data = await request.json()
    # TODO not "default". read the db client name from the user session (users should be able to select which db they want to use)
    known_records = await linker.get_known_records_map(
        request.app.db_clients["default"]
    )
    data = linker.insert_links(data, known_records)
    result = await request.app.db_clients["default"].store(data)
    if not result:
        return web.Response(status=500)
    return web.json_response({"data": result}, status=201)


async def put(request: web.Request) -> web.Response:
    data = await request.json()
    record_id = request.match_info.get("record_id")
    if not record_id or not ObjectId.is_valid(record_id):
        return web.Response(status=404)

    filter = {"_id": record_id}
    # TODO not "default". read the db client name from the user session (users should be able to select which db they want to use)
    known_records = await linker.get_known_records_map(
        request.app.db_clients["default"]
    )
    data = linker.insert_links(data, known_records)
    result = await request.app.db_clients["default"].update(filter, data)
    if not result:
        return web.Response(status=400)
    return web.json_response({"data": result}, status=200)


async def delete(request: web.Request) -> web.Response:
    data = await request.json()
    record_id = request.match_info.get("record_id")
    if not record_id or not ObjectId.is_valid(record_id):
        return web.Response(status=404)

    filter = {"_id": record_id}
    # TODO not "default". read the db client name from the user session (users should be able to select which db they want to use)
    known_records = await linker.get_known_records_map(
        request.app.db_clients["default"]
    )
    data = linker.insert_links(data, known_records)
    result = await request.app.db_clients["default"].update(filter, data)
    if not result:
        return web.Response(status=400)
    return web.json_response({"data": result}, status=200)
