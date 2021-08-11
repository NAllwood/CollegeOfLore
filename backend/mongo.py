import copy
import logging
import motor.motor_asyncio
from pymongo.errors import ServerSelectionTimeoutError
from aiohttp import web

LOG = logging.getLogger(__name__)


def get_app_key(type: str, key: str) -> str:
    if key == 'default':
        template = '{type}'
    else:
        template = '{type}_{name}'
    return template.format(type=type, name=key)


def test_connection(app: web.Application):
    for key, _ in app.config['mongodb'].items():
        key = get_app_key('mongo', key)
        try:
            app[key].is_mongos
        except ServerSelectionTimeoutError:
            LOG.error("Mongo-Client {key} is not connected!".format(key=key))


async def enable(app: web.Application):
    print("in enable!")
    if 'mongodb' not in app.config:
        raise AttributeError('mongodb config is missing')

    for key, client_attr in app.config['mongodb'].items():
        client_attr = copy.copy(client_attr)
        db = client_attr.pop('db')
        client = motor.motor_asyncio.AsyncIOMotorClient(**client_attr)

        app_key = get_app_key('mongo', key)
        app[app_key] = client  # "mongo" for connection "default"

        # disabled because we dont use directly the mongo client (and thus db) anyway
        # app_key = get_app_key('db', key)
        # app[app_key] = client[db]  # "db" for connection "default"

    test_connection(app)


async def disable(app: web.Application):

    for key, _ in app.config['mongodb'].items():
        key = get_app_key('mongo', key)
        app[key].close()

    LOG.debug('mongo disconnected')
