import click
import asyncio
import logging
from backend.mongo_migrations import migration_basics as basics

LOG = logging.getLogger(__name__)


async def init_collections():
    LOG.info("Initializing collections")
    config = basics.load_config()
    db = basics.get_mongo_db(config)

    collections = ["item", "location", "organization", "person"]
    for name in collections:
        await db.create_collection(name)


@click.command
async def main():
    await init_collections()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
