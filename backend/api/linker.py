import logging
from aiohttp import web
from posixpath import dirname
from typing import Any, Iterable, Tuple
from backend.db_clients.base_client import DBClient

LOG = logging.getLogger(__name__)


async def link_all(app: web.Application):
    db_client = app.db_clients["mongo"]
    known_records = await get_known_records_map(db_client)
    records = await db_client.find_many({})  # default coll is records
    for record in records:
        record_id = record.pop("_id")
        filter = {"_id": record_id}
        record = insert_links(record, known_records)
        await db_client.replace(filter, record)


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
        record.update({"multi": False})
        records_map[name] = record
    return records_map


def generate_str_from_iterable(it: Iterable):
    """Generator function that takes any Iterable and yields all (nested) occurrences of primitive types as str

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
            [name.capitalize() for name in record.get("names", [])]
            + ([record["last_name"]] if record.get("last_name") else [])
        )
    )
    # first and last name
    possible_names.add(
        " ".join(
            [record.get("names", [""])[0].capitalize()]
            + ([record["last_name"]] if record.get("last_name") else [])
        )
    )
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
    longest_subtext = None
    longest_index = -1
    for subtext in subtexts:
        found_index = text.find(subtext)
        # do not recursivley link links e.g. <a href="res"><a href="res">Res</a></a>
        if text[found_index - 2 : found_index] == '">':
            continue

        # if we match something for the first time
        # or we have already matched something, but also match a longer subtext at the same index
        if found_index >= 0 and (longest_index == -1 or longest_index == found_index):
            longest_subtext = subtext
            longest_index = found_index

    return (longest_subtext, longest_index)


def recursive_replace_substings_with_links(
    original_text: str, substings: Iterable, resource_name: str
) -> str:
    """Replaces the longest matching occurrences of names in the original text with corresponding links

    Args:
        original_text (str): the text in which the replacements should be made
        substings (Iterable): an iterable of substrings that should be replaced by links in the text
        resource_name (str): the name of the resource that should be linked

    Returns:
        str: the string in which all occurences of the substings are replaced by links
    """
    longest_matching_substring, _ = get_longest_matching_substring(
        original_text, substings
    )
    if not longest_matching_substring:
        return original_text

    link = f'<a href="{resource_name}">{longest_matching_substring}</a>'
    pre_text, _, post_text = original_text.partition(longest_matching_substring)
    return (
        pre_text
        + link
        + recursive_replace_substings_with_links(post_text, substings, resource_name)
    )


# TODO multi


def replace_text_with_links_for_records(
    original_text: str, replaced_str: str, replace_context: dict
):
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

        # avoid recursively inserting links into links by checking if a link already exists
        link = f'<a href="{replace_context["name_id"]}">{replaced_str.capitalize()}</a>'
        LOG.debug("NOTICE ME!!!!!!!!!!!!!!!!!!!!!")
        print(link, original_text, link in original_text)
        if link not in original_text:
            text = original_text.replace(replaced_str, link)
        return text

    # if type is person, they can have multiple names that can be replaced by a link
    possible_names = get_all_possible_names_from_record(replace_context)
    text = recursive_replace_substings_with_links(
        original_text, possible_names, replace_context["name_id"]
    )
    return text


def insert_links(new_record: dict, records_map: dict) -> dict:
    """Inserts links to other records into a given record by replacing all mentions with corresponding html links

    Args:
        new_record (dict): the record in which the links should be inserted
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record

    Returns:
        dict: a record in which all mentions of other records have been replaced by links
    """
    # we dont want to insert links for the record page we are currently on, so pop that entry from the map
    own_name = purify_name(new_record["name_id"])
    map_entry = records_map.pop(own_name, None)

    _, linked_record_ids_info = insert_links_into_infobox(
        new_record.get("infobox", {}), records_map
    )
    _, linked_record_ids_articles = insert_links_into_articles(
        new_record.get("articles"), records_map
    )

    new_record["linked_records"] = linked_record_ids_info
    new_record["linked_records"].extend(linked_record_ids_articles)

    # if there was no entry in the map (completely new record) then we don't have to restore.
    # TODO Update map function should be called after inserts that uses the DB so we get the _id of the new record in the map
    if map_entry:
        records_map[own_name] = map_entry

    return new_record


def insert_links_into_infobox(it: Iterable, records_map: dict) -> Tuple[Iterable, list]:
    """Recursively Inserts links into any iterable (used for the 'infobox' part of records)

    Args:
        new_record (dict): the record in which the links should be inserted
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record

    Returns:
        a tuple consisting of the initial Iterable with replaced texts, a list containing the ObjectIDs of all DB entries that were linked to
    """
    linked_ids = []
    if isinstance(it, dict):
        for key, value in it.items():
            new_item, new_ids = insert_links_into_infobox(value, records_map)
            it[key] = new_item
            linked_ids.extend(new_ids)
        return it, linked_ids

    if isinstance(it, list):
        for index, entry in enumerate(it):
            new_entry, new_ids = insert_links_into_infobox(entry, records_map)
            it[index] = new_entry
            linked_ids.extend(new_ids)
        return it, linked_ids

    if isinstance(it, str):
        word = it.lower()
        if word not in records_map:
            return (it, linked_ids)
        linked_ids.append(records_map[word].get("_id"))
        return (
            replace_text_with_links_for_records(word, word, records_map[word]),
            linked_ids,
        )

    if isinstance(it, int) or isinstance(it, float):
        return str(it), linked_ids

    return None, linked_ids


def insert_links_into_articles(
    articles: dict, records_map: dict
) -> Tuple[Iterable, list]:
    """Inserts links only into the 'articles' part of records

    Args:
        articles (dict): amapping of titles to text
        records_map (dict): a mapping of strings that represent what is identified as a "mention" to general information of the corresponding record

    Returns:
        a tuple consisting of the initial Iterable with replaced texts, a list containing the ObjectIDs of all DB entries that were linked to
    """
    # directly access artcles with the key because we want to continuously change articles
    # (build on prev replacements), not a static copy
    if not articles:
        return

    linked_ids = []

    for title in articles.keys():
        # (going through it this way makes more sense than going through every word in the article
        # (as long as there are fewer db entries than average words in an article))
        # go through every entry of known records and replace each mention with a link
        for key, replace_context in records_map.items():
            # check if the purified unique name of another record can be found in the text
            # capitalize because we only want to replace capitalized words (names)
            article = articles.get(title, "")
            reference_word = key.capitalize()
            if not article or reference_word not in article:
                continue

            articles[title] = replace_text_with_links_for_records(
                article, reference_word, replace_context
            )
            linked_ids.append(replace_context.get("_id"))

    return articles, linked_ids
