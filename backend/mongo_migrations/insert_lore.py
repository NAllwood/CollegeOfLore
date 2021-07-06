
import os
import asyncio
import click
import logging
from backend.mongo_migrations import migration_basics as basics


LOG = logging.getLogger(__name__)


async def insert_lore():
    LOG.info("Inserting documents from local files")
    LORE_FOLDER_NAME = "lore"
    ALLOWED_DIRS = ["item", "location", "organization", "person"]

    config = basics.load_config()
    db = basics.get_mongo_db(config)

    for root, _, files in os.walk(os.path.join(basics.BASE_PATH, LORE_FOLDER_NAME), topdown=False):
        for name in files:
            article_category = next(
                (dir_name for dir_name in ALLOWED_DIRS if dir_name in root), None)
            if not article_category:
                LOG.warn(
                    f"Found file with invalid category at '{root} /{name}'. Skipping this.")
                continue

            file_name = os.path.splitext(name)[0]

            document = basiscs.load_yaml(os.path.join(root, name))
            if not "name_id" in document:
                document["name_id"] = file_name

            LOG.info(f"have {name}")
            if not basiscs.exists(db[article_category], {"name_id": document["name_id"]}):
                LOG.info(
                    f"Inserting {file_name} into the database under {article_category}")
                db[article_category].insert_one(document)


@click.command()
async def main():
    await insert_lore()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
