import logging
import sys
import asyncio
import yaml
import os
import jinja2
import aiohttp_jinja2
from functools import partial
from aiohttp import web
from . import routes, mongo, linker
from backend.db_clients.mongo_client import MongoClient
from backend import lang


BASE_PATH = os.path.dirname(__file__)
LOG = logging.getLogger(__name__)


class Application(web.Application):
    def __init__(self, config=None, debug=False, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.load_config(config)
        self.setup_attributes()
        self.setup_templating()
        self.load_plugins()
        routes.register(self)
        setup_logging()
        # probably needs to happen AFTER "load_plugins" to use underlying database clients
        self.on_startup.append(connect_db_clients)
        #di.GLOBAL_SCOPE = self

    def load_config(self, config):
        if config:
            self.config = config
            return

        try:
            with open(os.path.join(BASE_PATH, "config_default.yml"), "r") as ymlfile:
                self.config = yaml.load(ymlfile, Loader=yaml.Loader)
        except FileNotFoundError:
            raise FileNotFoundError("config file missing!")

    def load_plugins(self):
        LOG.info('loading plugins')
        # creates mongo client for each connection specified in config (creates client and appends it to app)
        self.on_startup.append(mongo.enable)
        self.on_cleanup.append(mongo.disable)

    #     # wrapped db connection in "LoreClient"
    #     # self.cleanup_ctx.append(mongo.enable)
    #     if debug:
    #         # self.cleanup_ctx.append(blower_test_server.enable)
    #         pass

    def setup_attributes(self):
        # needed for local loading of templates, statics, ...
        self.base_path = BASE_PATH

        # needed like this for builtin jinja2 static lookup function
        self['static_root_url'] = '/static'

        # needed to store all (abstracted) database clients
        self.db_clients = {}

        # TODO
        # self.linking_dict = linker.get_all_records()

    def setup_templating(self):
        loader = jinja2.FileSystemLoader(os.path.join(BASE_PATH, 'templates/'))

        # context processors allow to define functions to automatically create a rendering context from the request
        # maybe if we need universal processors in the future (username, auth, login, ...)
        # processors = [context_processors.get_render_context, aiohttp_jinja2.request_processor]
        # ... context_processors=processors, ...
        aiohttp_jinja2.setup(self, loader=loader)

        env = aiohttp_jinja2.get_env(self)

        # needed for automatic translation (makes translate function availabe in templates)
        language = "DE"
        locales = lang.load_locale()
        translate = partial(
            lang.translate, locales.get(language, {}))
        env.globals.update(translate=translate)


async def connect_db_clients(app: web.Application):
    """create a new DBClient that abstacts from the actual db used for each connection"""
    # currently mongo only
    for mongo_name in app.config["mongodb"].keys():
        MongoClient(app, mongo_name)

# used for aiohttp-devtools


def create_app(loop=None, config=None, debug=False):
    if loop is None:
        loop = asyncio.get_event_loop()
    return Application(loop=loop, config=config, debug=debug)


def setup_logging():
    """
    configure logger to include date and log on stdout
    :param bool warnings: Whether to show warnings
    :param logging.Logger logger: logger that needs to be configured
    """

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[handler])


def main(host=None, port=None, config=None):
    web.run_app(create_app(config=config), host=host, port=port)


if __name__ == '__main__':
    main()
