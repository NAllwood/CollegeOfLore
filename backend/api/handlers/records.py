import logging
import aiohttp_jinja2
from aiohttp import web
from bson import ObjectId
from backend.api import linker, context_processor
from backend.api.handlers import error_pages
from backend.api.errors import RequestError

LOG = logging.getLogger(__name__)


async def get(request: web.Request) -> web.Response:
    context = await context_processor.get_context(request)
    if not context:
        return error_pages.get_error_page(request, RequestError.not_found)

    record_type = context.get("type")
    if not record_type:
        return error_pages.get_error_page(request, RequestError.corrupt)

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
        return RequestError.service_unavailable
    return {"data": result, "status": 201}


async def put(request: web.Request) -> web.Response:
    data = await request.json()
    record_id = request.match_info.get("record_id")
    if not record_id or not ObjectId.is_valid(record_id):
        return RequestError.malformed_request

    filter = {"_id": record_id}
    # TODO not "default". read the db client name from the user session (users should be able to select which db they want to use)
    known_records = await linker.get_known_records_map(
        request.app.db_clients["default"]
    )
    data = linker.insert_links(data, known_records)
    result = await request.app.db_clients["default"].update(filter, data)
    if not result:
        return RequestError.service_unavailable
    return {"data": result, "status": 200}


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
        return RequestError.service_unavailable
    return {"data": result, "status": 200}
