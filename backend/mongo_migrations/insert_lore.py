import os
import asyncio
import logging
from backend.mongo_migrations import migration_basics as basics
from backend.mongo_migrations.migration_mongo_client import MigrationMongoClient
from backend import linker


LOG = logging.getLogger(__name__)


async def insert_lore():
    LOG.info("Inserting documents from local files")
    LORE_FOLDER_NAME = "lore"
    # ALLOWED_DIRS = ["item", "location", "organization", "person"]

    config = basics.load_config()
    db = basics.get_mongo_db(config)
    db_client = MigrationMongoClient(db)
    COLLECTION_NAME = "records"
    coll = db[COLLECTION_NAME]

    for root, _, files in os.walk(
        os.path.join(basics.BASE_PATH, LORE_FOLDER_NAME), topdown=False
    ):
        for name in files:
            # update known records after every insert
            known_records = await linker.get_known_records_map(db_client)
            file_name = os.path.splitext(name)[0]

            document = basics.load_yaml(os.path.join(root, name))
            if not "name_id" in document:
                document["name_id"] = file_name

            LOG.info(f"have {name}")
            if not await basics.exists(coll, {"name_id": document["name_id"]}):
                LOG.info("Linking document")
                document = linker.insert_links(document, known_records)
                LOG.info(
                    f"Inserting {file_name} into the database under {COLLECTION_NAME}"
                )
                await coll.insert_one(document)
            else:
                LOG.info("Record already exists in the dabase!")


async def main():
    basics.setup_logging()
    await insert_lore()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
