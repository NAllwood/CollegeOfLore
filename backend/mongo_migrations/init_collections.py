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
    
    db.createCollection("users", {
        validator: {$jsonSchema: {
            bsonType: "object",
            required: ["name", "hashed_pw", "lores_owned", "lores_access"],
            properties: {
                name: {
                    bsonType: "string",
                    description: "username"
                },
                hashed_pw: {
                    bsonType: "string",
                    description: "hashed and salted bcrypt password"
                },
                lores_owned: {
                    bsonType: "array",
                    description: "a list of lores that the user owns"
                },
                lores_access: {
                    bsonType: "array",
                    description: "a list of lores that the user can access"
                },
                "is_admin": {
                    bsonType: "bool",
                    description: "states whether user is an admin of the system"
                }
            }
        }
        }
    })

    db.createCollection("lores", {
        validator: {$jsonSchema: {
            bsonType: "object",
            required: ["name", "masters", "members"],
            properties: {
                name: {
                    bsonType: "string",
                    description: "name of the lore (world/game/table)"
                },

                masters: {
                    bsonType: "array",
                    description: "a list referencing the users that are masters of this lore"
                },
                members: {
                    bsonType: "array",
                    description: "a list referencing the users that share this lore"
                },
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
