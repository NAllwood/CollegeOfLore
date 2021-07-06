import motor.motor_asyncio
import yaml
import logging
import os
import backend
from typing import Any

BASE_PATH = os.path.dirname(backend.__file__)
LOG = logging.getLogger(__name__)


def load_config():
    LOG.info("loading config")
    try:
        with open(os.path.join(BASE_PATH, "config_default.yml"), "r") as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.Loader)
    except FileNotFoundError:
        raise FileNotFoundError("config file missing!")


def load_yaml(path: str):
    LOG.info("Trying to load yaml {path}")
    try:
        with open(path, "r") as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.Loader)
    except FileNotFoundError:
        raise FileNotFoundError("lore file is missing!")


def get_mongo_db(config: dict) -> motor.motor_asyncio.AsyncIOMotorDatabase:
    LOG.info("initializing mongodb connection")
    if 'mongodb' not in config:
        raise AttributeError('mongodb config is missing')

    config = config["mongodb"]["default"]

    host = config["host"]
    port = config["port"]
    db_name = config["db"]
    client = motor.motor_asyncio.AsyncIOMotorClient(host=host, port=port)
    return client[db_name]


async def exists(coll: motor.motor_asyncio.AsyncIOMotorCollection, doc_filter: dict) -> bool:
    LOG.info(f"Checking if document with {doc_filter} exists...")
    if coll.find(doc_filter).count() > 0:
        LOG.info("Yes")
        return True
    LOG.info("No")
    return False
