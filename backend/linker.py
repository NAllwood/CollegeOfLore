import logging
import copy
from posixpath import dirname
from typing import Any, Generator, Iterable, Tuple
from backend.db_clients.base_client import DBClient

LOG = logging.getLogger(__name__)


def purify_name(name: str) -> str:
    """Removes all digits and parts after a '_' from the string

    Args:
        name (str): the string to purify

    Returns:
        str: purified string
    """
    if not name:
        return ""

    name = name.split("_")[0]
    name = "".join(i for i in name if not i.isdigit())
    return name


async def get_known_records_map(db_client: DBClient) -> dict:
    """Fetches a projection of all known records from a database collection using the provided client

    Args:
        db_client (DBClient): A database client

    Returns:
        dict: Mapping of the "purified name_id (no digits or '_') to record fields (["_id", "name_id", "type", "names", "last_name"])
    """
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


def generate_str_from_iterable(it: Iterable):
    """Generator function that takes any Iterable and yields all (nested) ocurrences of primitive types as str

    Args:
        it (Iterable): iterable datatype

    Yields:
        Iterator[str]: found primitive datatype (str, int, float) as str
    """
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
    """forms and returns all possible proper names for a person from a record

    Args:
        record (dict): a record (should contain at least 'names')

    Returns:
        set: [description]
    """
    possible_names = set()
    # all names (two list of str to single str into set) e.g. "Nevin Myron Allwood"
    possible_names.add(
        " ".join(
            [name.capitalize() for name in record.get("names", [])] +
            ([record["last_name"].capitalize()]
                if record.get("last_name") else [])
        )
    )
    # first and last name
    possible_names.add(" ".join([record.get("names", [""])[0].capitalize(
    )] + ([record["last_name"].capitalize()] if record.get("last_name") else [])))
    # all first and second names e.g. "Nevin Myron"
    possible_names.add(" ".join([*record.get("names", [])]))
    # only first name e.g. "Nevin"
    possible_names.add(record.get("names", [""])[0])

    possible_names.remove("") if "" in possible_names else None
    return possible_names


def get_longest_matching_substring(text: str, substrings: Iterable) -> Tuple[str, int]:
    """takes a sting and an Iterable of substrings and returns a tuple of the longest matching one and its index or (None, -1).

    Args:
        text (str): the text that should be searched for matches
        substrings (Iterable): the substrings that should be searched for

    Returns:
        Tuple[str, int]: longest match as string + its index in the text or (None, -1) 
    """
    subtexts = sorted(substrings, key=len)
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


def recursive_replace_substings_with_links(original_text: str, substings: Iterable, resource_name: str) -> str:
    """Replaces the longest matching occurrences of names in the original text with corresponding links

    Args:
        original_text (str): the text in which the replacements should be made
        substings (Iterable): an iterable of substrings that should be replaced by links in the text
        resource_name (str): the name of the resource that should be linked

    Returns:
        str: the string in which all occurences of the substings are replaced by links
    """
    longest_matching_substring, _ = get_longest_matching_substring(
        original_text, substings)
    if not longest_matching_substring:
        return original_text

    link = f'<a href="records/{resource_name}">{longest_matching_substring}</a>'
    pre_text, _, post_text = original_text.partition(
        longest_matching_substring)
    return pre_text + link + recursive_replace_substings_with_links(post_text, substings, resource_name)


# TODO multi
def replace_text_with_links_for_records(original_text: str, replaced_str: str, replace_context: dict):
    """Replaces mentions of other records within a given text with links based on the linked record type

    Args:
        original_text (str): the original text in which replacements shall be made
        replace_text (str): the text that is to be replaced with a link
        replace_context (dict): general information about the record that should be linked to

    Returns:
        [type]: the text in which the specified strings are replaced by links
    """
    # if the type of the found record is not "person", replace found mentions of the existing record with a link
    if replace_context["type"] != "person":
        link = f'<a href="records/{replace_context["name_id"]}">{replaced_str.capitalize()}</a>'
        text = original_text.replace(replaced_str.capitalize(), link)
        return text

    # if type is person, they can have multiple names that can be replaced by a link
    possible_names = get_all_possible_names_from_record(replace_context)
    text = recursive_replace_substings_with_links(
        original_text, possible_names, replace_context["name_id"])
    return text


async def insert_links(new_record: dict, records_map: dict) -> dict:
    """Inserts links to other records into a given record by replacing all mentions with corresponding html links

    Args:
        new_record (dict): the record in which the links should be inserted
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record

    Returns:
        dict: a record in which all mentionings of other records have been replaced by links 
    """
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


def insert_links_into_infobox(new_record: dict, records_map: dict):
    """Inserts links only into the 'infobox' part of records

    Args:
        new_record (dict): the record in which the links should be inserted
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record
    """
    for word in generate_str_from_iterable(new_record):
        if word not in records_map:
            continue

        word = replace_text_with_links_for_records(
            word, word, records_map[word])


def insert_links_into_articles(new_record: dict, records_map: dict):
    """Inserts links only into the 'articles' part of records

    Args:
        new_record (dict): the record in which the links should be inserted
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record
    """
    for article in new_record["articles"]:
        for text in article:
            # go through every entry of known records and replace each mention with a link
            for key, items in records_map.items():
                # check if the purified unique name of another record can be found in the text
                if key not in text and key.capitalize() not in text:
                    continue

                text = replace_text_with_links_for_records(text, key, items)
