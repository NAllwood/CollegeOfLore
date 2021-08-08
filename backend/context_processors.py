import logging
import os
import yaml
import typing
from aiohttp import web


LOG = logging.getLogger(__name__)

# legacy from file based initial exploration
# def get_local_context(base_path: str, article_type: str, name: str) -> typing.Optional[dict]:
#     """Creates path from parameters and attempts to locally find the corresponding. '.yml' file.

#     Args:
#         base_path (str): base path of the filesystem
#         article_type (str): type of article to be loaded (person/place/item...)
#         name (str): name of the article

#     Returns:
#         dict/None: the parsed dict, or None, if the yml was not found.
#     """

#     if name is None or article_type is None:
#         return None

#     try:
#         yaml_path = os.path.join(
#             base_path, "lore", "{}".format(article_type), "{}.yml".format(name))
#         with open(yaml_path, "r") as ymlfile:
#             return yaml.load(ymlfile, Loader=yaml.Loader)
#     except FileNotFoundError:
#         LOG.warning("yaml file missing for '{}'".format(yaml_path))
#         return {}


async def get_record_context(request: web.Request) -> typing.Optional[dict]:
    """Gets the specific information required to render an article page.

    Args:
        request (web.Request): the client's web request

    Returns:
        dict/None: a dict containing the article information, or None
    """

    resource_category = request.match_info.get('resource_category')
    record_name_id = request.match_info.get('name')

    if not resource_category or not record_name_id:
        return {}

    # TODO not "default". read the db client name from the user session (users should be able to select which db they want to use)
    record = await request.app.db_clients["default"].find({"name_id": record_name_id})
    return record
