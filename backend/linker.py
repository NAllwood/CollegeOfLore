import logging
import copy
from posixpath import dirname
from typing import Any, Generator, Iterable, Tuple
from backend.db_clients.base_client import DBClient

LOG = logging.getLogger(__name__)


def purify_name(name: str) -> str:
    if not name:
        return ""

    name = name.split("_")[0]
    name = "".join(i for i in name if not i.isdigit())
    return name


async def get_all_records(db_client: DBClient) -> dict:
    records_map = {}

    filter = {}
    projection = ["_id", "name_id", "type", "names", "last_name"]
    records = await db_client.find_many(filter, projection)
    for record in records:
        name = purify_name(record["name_id"])
        if name in records_map:
            records_map[name]["multi"] = True
            continue

        records_map[name] = {"type": record["type"], "multi": False}
    return records


def generate_str_from_iterable(it: Iterable) -> str:
    if isinstance(it, dict):
        for value in it.values():
            yield from generate_str_from_iterable(value)

    if isinstance(it, list):
        for entry in it:
            yield from generate_str_from_iterable(entry)

    if isinstance(it, str):
        yield it

    if isinstance(it, int) or isinstance(it, float):
        yield str(it)


def get_all_possible_names_from_record(record: dict) -> set:
    possible_names = set()
    # all names (two list of str to single str into set) e.g. "Nevin Myron Allwood"
    possible_names.add(
        " ".join(
            [name.capitalize() for name in record["names"]] +
            ([record["last_name"].capitalize()]
                if record["last_name"] else [])
        )
    )
    # first and last name
    possible_names.add(" ".join([record["names"][0].capitalize(
    )] + ([record["last_name"].capitalize()] if record["last_name"] else [])))
    # all first and second names e.g. "Nevin Myron"
    possible_names.add(" ".join([*record["names"]]))
    # only first name e.g. "Nevin"
    possible_names.add(record["names"][0])

    return possible_names


def get_longest_match(text: str, subtexts: Iterable) -> Tuple[str, int]:
    subtexts = sorted(subtexts, key=len)
    print(subtexts)
    longest_subtext = None
    longest_index = -1

    for subtext in subtexts:
        found_index = text.find(subtext)
        # if we match something for the first time
        # or we have already matched something, but also match a longer subtext at the same index
        if found_index >= 0 and (longest_index == -1 or longest_index == found_index):
            longest_subtext = subtext
            longest_index = found_index

    return (longest_subtext, longest_index)


def recursive_replace_names_to_links(original_text: str, names: Iterable, name_id: str) -> str:
    longest_matching_name, _ = get_longest_match(original_text, names)
    if not longest_matching_name:
        return original_text

    link = f'<a href="records/{name_id}">{longest_matching_name}</a>'
    pre_text, _, post_text = original_text.partition(longest_matching_name)
    return pre_text + link + recursive_replace_names_to_links(post_text, names, name_id)


def replace_text_of_record(original_text: str, replace_text: str, replace_context: dict):  # TODO multi
    text = copy.copy(original_text)
    # if the type of the found record is not "person", replace found mentions of the existing record with a link
    if replace_context["type"] != "person":
        link = f'<a href="records/{replace_context["name_id"]}">{replace_text.capitalize()}</a>'
        text = text.replace(replace_text.capitalize(), link)
        return text

    # if type is person, they can have multiple names that can be replaced by a link
    possible_names = get_all_possible_names_from_record(replace_context)
    text = recursive_replace_names_to_links(
        text, possible_names, replace_context["name_id"])
    return text


async def insert_links(new_record: dict, records_map: dict) -> dict:
    # we dont want to insert links for the record page we are currently on, so pop that entry from the map
    own_name = purify_name(new_record["name_id"])
    map_entry = records_map.pop(own_name, None)

    insert_links_into_infobox(new_record, records_map)
    insert_links_into_articles(new_record, records_map)

    # if there was no entry in the map (completely new record) then we don't have to restore.
    # TODO Update map function should be called after inserts that uses the DB so we get the _id of the new record in the map
    if map_entry:
        records_map[own_name] = map_entry

    return new_record


def insert_links_into_infobox(new_record: dict, records_map: dict) -> dict:
    for word in generate_str_from_iterable(new_record):
        if word not in records_map:
            continue

        word = replace_text_of_record(word, word, records_map[word])


def insert_links_into_articles(new_record: dict, records_map: dict) -> dict:
    for article in new_record["articles"]:
        for text in article:
            # go through every entry of known records and replace each mention with a link
            for key, items in records_map.items():
                # check if the purified unique name of another record can be found in the text
                if key not in text and key.capitalize() not in text:
                    continue

                text = replace_text_of_record(text, key, items)
