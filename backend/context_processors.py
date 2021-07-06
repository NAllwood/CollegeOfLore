import logging
import os
import yaml
import typing
from aiohttp import web


LOG = logging.getLogger(__name__)


def get_mongo_context():
    pass


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
        return {}


async def get_render_context(request: web.Request) -> typing.Optional[dict]:
    """Gets the specific information required to render an article page.

    Args:
        base_path (str): base path of the filesystem
        article_type (str): type of article to be loaded (person/place/item...)
        name (str): name of the article

    Returns:
        dict/None: a dict containing the article information, or None
    """

    # TODO USE MONGODB FOR INFO STORAGE LATER

    article_type = request.match_info.get('article_type')
    article_name = request.match_info.get('name')

    if not article_type or not article_name:
        return {}

    return get_local_context(
        request.app.base_path,
        article_type,
        article_name)
