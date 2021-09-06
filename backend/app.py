import logging
import sys
import asyncio
import yaml
import os
import jinja2
import aiohttp_jinja2
import base64
from functools import partial
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from . import mongo
from backend.api import routes
from backend.db_clients.mongo_client import MongoClient
from backend import lang
from backend.api import middlewares


BASE_PATH = os.path.dirname(__file__)
LOG = logging.getLogger(__name__)


class Application(web.Application):
    def __init__(self, config=None, debug=False, **kwargs):
        super(Application, self).__init__(**kwargs)
        self.load_config(config)
        self.setup_attributes()
        self.setup_templating()
        self.load_plugins()
        self.setup_sessions()
        self.add_middlewares()
        routes.register(self)
        setup_logging()
        # di.GLOBAL_SCOPE = self

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
        LOG.info("loading plugins")
        # creates mongo client for each connection specified in config
        # not using cleanup context because
        self.on_startup.append(mongo.enable)
        self.on_cleanup.append(mongo.disable)

        # creates client wrappers and appends them to app
        # probably needs to happen AFTER enabling underlying db clinets (mongo)
        self.on_startup.append(self.connect_db_clients)

    def setup_attributes(self):
        # needed for local loading of templates, statics, ...
        self.base_path = BASE_PATH

        # needed like this for builtin jinja2 static lookup function
        self["static_root_url"] = "/static"

        # needed to store all (abstracted) database clients (set in load_plugins)
        self.db_clients = {}

    def setup_templating(self):
        loader = jinja2.FileSystemLoader(os.path.join(BASE_PATH, "templates/"))

        # context processors allow to define functions to automatically create a rendering context from the request
        # maybe if we need universal processors in the future (username, auth, login, ...)
        # processors = [context_processors.get_render_context, aiohttp_jinja2.request_processor]
        # ... context_processors=processors, ...
        aiohttp_jinja2.setup(self, loader=loader)

        env = aiohttp_jinja2.get_env(self)

        # needed for automatic translation (makes translate function availabe in templates)
        language = "DE"
        locales = lang.load_locale()
        translate = partial(lang.translate, locales.get(language, {}))
        env.globals.update(translate=translate)

    def setup_sessions(self):
        # session setup. needs custom encoder+decoder to store object ids
        fernet_key = self.config['session']['secret']
        secret_key = base64.urlsafe_b64decode(fernet_key)
        encrypted_storage = EncryptedCookieStorage(secret_key)
        setup(self, encrypted_storage)

    def add_middlewares(self):
        self.middlewares.extend([middlewares.auth_middleware])

    async def connect_db_clients(self, app: web.Application):
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
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[handler])


def main(host=None, port=None, config=None):
    web.run_app(create_app(config=config), host=host, port=port)


if __name__ == "__main__":
    main()
