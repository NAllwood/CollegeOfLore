import click
import asyncio
import logging
from backend.mongo_migrations import migration_basics as basics

LOG = logging.getLogger(__name__)

"""
    db.createCollection("records", {
        validator: {$jsonSchema: {
            bsonType: "object",
            required: ["type", "name_id", "infobox", "articles"],
            properties: {
                type: {
                    bsonType: "string",
                    description: "type of the record (e.g. person, item, ..."
                },
                name_id: {
                    bsonType: "string",
                    description: "name that uniquely identifies the record"
                },
                infobox: {
                    bsonType: "object"
                },
                articles: {
                    bsonType: "array",
                    description: "array of text articles"
                }
            }
        }
        }
    })
    """


# async def init_collections():
#     LOG.info("Initializing collections")
#     config = basics.load_config()
#     db = basics.get_mongo_db(config)

# collections = ["item", "location", "organization", "person"]
# for name in collections:
#     await db.create_collection(name)


# @click.command
# async def main():
#     await init_collections()


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
