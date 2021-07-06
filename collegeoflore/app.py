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
from collegeoflore import lang


BASE_PATH = os.path.dirname(__file__)

LOG = logging.getLogger(__name__)


class Application(web.Application):
    def __init__(self, config=None, debug=False, **kwargs):
        super(Application, self).__init__(**kwargs)

        loader = jinja2.FileSystemLoader(os.path.join(BASE_PATH, 'templates/'))
        aiohttp_jinja2.setup(self, loader=loader)

        self.config = config
        if self.config is None:
            try:
                with open(os.path.join(BASE_PATH, "config_default.yml"), "r") as ymlfile:
                    self.config = yaml.load(ymlfile, Loader=yaml.Loader)
            except FileNotFoundError:
                LOG.error("config file missing!")
                exit

        self['app_config'] = self.config
        self['base_path'] = BASE_PATH
        self['static_root_url'] = '/static'
        self['lang'] = "DE"
        self['locales'] = lang.load_locale()
        self['translate'] = partial(
            lang.translate, self['locales'].get(self['lang'], {}))

        self.load_plugins(debug)

        routes.register(self)
        linker.get_all_articles_dict()

        #di.GLOBAL_SCOPE = self

        setup_logging()

    def load_plugins(self, debug: bool):
        LOG.info('load plugins')
        self.cleanup_ctx.append(mongo.enable)
        # self.cleanup_ctx.append(db_socket_server.enable)
        if debug:
            # self.cleanup_ctx.append(blower_test_server.enable)
            pass


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
