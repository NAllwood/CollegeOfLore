
import os
import asyncio
import click
import logging
from backend.mongo_migrations import migration_basics as basics


LOG = logging.getLogger(__name__)


async def insert_lore():
    LOG.info("Inserting documents from local files")
    LORE_FOLDER_NAME = "lore"
    # ALLOWED_DIRS = ["item", "location", "organization", "person"]

    config = basics.load_config()
    db = basics.get_mongo_db(config)

    for root, _, files in os.walk(os.path.join(basics.BASE_PATH, LORE_FOLDER_NAME), topdown=False):
        for name in files:
            # article_category = next(
            #     (dir_name for dir_name in ALLOWED_DIRS if dir_name in root), None)
            # if not article_category:
            #     LOG.warn(
            #         f"Found file with invalid category at '{root} /{name}'. Skipping this.")
            #     continue
            # collection_name = article_category

            collection_name = "records"

            file_name = os.path.splitext(name)[0]

            document = basics.load_yaml(os.path.join(root, name))
            if not "name_id" in document:
                document["name_id"] = file_name

            LOG.info(f"have {name}")
            if not await basics.exists(db[collection_name], {"name_id": document["name_id"]}):
                LOG.info(
                    f"Inserting {file_name} into the database under {collection_name}")
                db[collection_name].insert_one(document)
            else:
                LOG.info("Record already exists in the dabase!")


async def main():
    basics.setup_logging()
    await insert_lore()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
