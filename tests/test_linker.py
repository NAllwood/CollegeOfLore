import pytest
import yaml
import os
from backend import linker
from bson import ObjectId

## Fixtures ##


@pytest.fixture
def example_record():
    return {
        "key1": "one",
        "key2": 1,
        "key3": {
            "key3.1": "One",
            "key3.2": 2,
            "key3.3": ["two", 3, {"key3.3.1": 3.31}],
        },
        "key4": [4.0, 4, "three"],
    }


@pytest.fixture
def expected_strings_in_example_record():
    return set(
        [
            "one",
            "1",
            "One",
            "2",
            "two",
            "3",
            "3.31",
            "4.0",
            "4",
            "three",
        ]
    )


@pytest.fixture
def replace_context_person():
    return {
        "one": {
            "type": "person",
            "names": ["One", "Two"],
            "last_name": "Three",
            "name_id": "one",
        }
    }


@pytest.fixture
def replace_context_nolen():
    return {
        "umaron": {
            "type": "location",
            "name_id": "umaron",
            "_id": ObjectId("611be36d862be82b4a41ee68"),
        },
        "garrett": {
            "type": "person",
            "names": ["Garrett"],
            "last_name": "von Danamark",
            "name_id": "garrett",
            "_id": ObjectId("666f6f2d6261722d71757578"),
        },
        "nolen": {
            "type": "person",
            "names": ["Nolen", "Constantin", "Lepidus"],
            "last_name": "Silverbridge",
            "name_id": "nolen2",
            "multi": True,
            "_id": ObjectId("0123456789ab0123456789ab"),
        },
    }


@pytest.fixture
def replace_context_not_person():
    return {"two": {"type": "location", "name_id": "two2"}}


@pytest.fixture
def nolen_possible_names():
    return set(
        [
            "Nolen",
            "Nolen Constantin Lepidus",
            "Nolen Constantin Lepidus Silverbridge",
            "Nolen Silverbridge",
        ]
    )


@pytest.fixture
def nolen_record():
    directory = os.path.dirname(__file__)
    try:
        with open(os.path.join(directory, "resources", "nolen2.yml"), "r") as ymlfile:
            return yaml.load(ymlfile, Loader=yaml.Loader)
    except FileNotFoundError:
        raise FileNotFoundError("config file missing!")


## Tests ##


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("test", "test"),
        ("test test", "test test"),
        ("test_test", "test"),
        ("test1", "test"),
        ("test22_test3", "test"),
        ("", ""),
        (None, ""),
    ],
)
def test_purify_name(test_input, expected):
    assert linker.purify_name(test_input) == expected


def test_generate_str_from_iterable(example_record, expected_strings_in_example_record):
    for word in linker.generate_str_from_iterable(example_record):
        expected_strings_in_example_record.remove(word)

    assert expected_strings_in_example_record == set()


def test_get_all_possible_names_from_record(nolen_record, nolen_possible_names):
    assert (
        linker.get_all_possible_names_from_record(nolen_record) == nolen_possible_names
    )


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("Seine Freunde nannten ihn Nolen.", ("Nolen", 26)),
        (
            "Getauft wurde er Nolen Constantin Lepidus.",
            ("Nolen Constantin Lepidus", 17),
        ),
        (
            "Doch Nolen Constantin Lepidus Silverbridge war sein ganzer Name.",
            ("Nolen Constantin Lepidus Silverbridge", 5),
        ),
    ],
)
def test_get_longest_matching_substring(input_text, expected, nolen_possible_names):
    result = linker.get_longest_matching_substring(input_text, nolen_possible_names)
    assert result == expected


@pytest.mark.parametrize(
    "input_text, name_id, expected",
    [
        ("Nolen", "nolen2", '<a href="nolen2">Nolen</a>'),
        (
            "Der Text vor Nolen und der danach",
            "nolen2",
            'Der Text vor <a href="nolen2">Nolen</a> und der danach',
        ),
        (
            "Doch Nolen Constantin Lepidus Silverbridge war sein ganzer Name.",
            "nolen2",
            'Doch <a href="nolen2">Nolen Constantin Lepidus Silverbridge</a> war sein ganzer Name.',
        ),
    ],
)
def test_recursive_replace_substings_with_links(
    input_text, name_id, expected, nolen_possible_names
) -> str:
    text = linker.recursive_replace_substings_with_links(
        input_text, nolen_possible_names, name_id
    )
    assert text == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("one", "one"),
        ("One", '<a href="one">One</a>'),
        ("One Two", '<a href="one">One Two</a>'),
        ("One Three", '<a href="one">One Three</a>'),
        ("One Two Three", '<a href="one">One Two Three</a>'),
        ("One two Three", '<a href="one">One</a> two Three'),
        ("minusOnetwo", 'minus<a href="one">One</a>two'),
        (
            "sometext. One. someothertext",
            'sometext. <a href="one">One</a>. someothertext',
        ),
    ],
)
def test_replace_text_of_record_person(input, expected, replace_context_person):
    # text to replace is irrelevant for persons becaus the names are replaced
    replaced = linker.replace_text_with_links_for_records(
        input, "", replace_context_person.get("one")
    )
    assert replaced == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        ("two", "two"),
        ("Two", '<a href="two2">Two</a>'),
        ("One Two", 'One <a href="two2">Two</a>'),
        ("minusTwoone", 'minus<a href="two2">Two</a>one'),
        (
            "sometext. Two. someothertext",
            'sometext. <a href="two2">Two</a>. someothertext',
        ),
    ],
)
def test_replace_text_of_record_not_person(input, expected, replace_context_not_person):
    replaced = linker.replace_text_with_links_for_records(
        input, "Two", replace_context_not_person.get("two")
    )
    assert replaced == expected


def test_insert_links_into_infobox(nolen_record, replace_context_nolen):
    assert nolen_record["infobox"]["biographical_info"]["origin"] == "Umaron"
    _, linked_ids = linker.insert_links_into_infobox(
        nolen_record["infobox"], replace_context_nolen
    )
    assert (
        nolen_record["infobox"]["biographical_info"]["origin"]
        == '<a href="umaron">Umaron</a>'
    )

    assert ObjectId("611be36d862be82b4a41ee68") in linked_ids


def test_insert_links_into_articles(nolen_record, replace_context_nolen):
    assert "Garrett von Danamark" in nolen_record["articles"]["relationships"]
    _, linked_ids = linker.insert_links_into_articles(
        nolen_record["articles"], replace_context_nolen
    )
    assert (
        '<a href="garrett">Garrett von Danamark</a>'
        in nolen_record["articles"]["relationships"]
    )
    assert ObjectId("666f6f2d6261722d71757578") in linked_ids


def test_insert_links(nolen_record, replace_context_nolen):
    assert nolen_record["infobox"]["biographical_info"]["origin"] == "Umaron"
    assert "Garrett von Danamark" in nolen_record["articles"]["relationships"]
    assert nolen_record["articles"]["description"].find("Nolen") == 0

    linker.insert_links(nolen_record, replace_context_nolen)

    assert (
        nolen_record["infobox"]["biographical_info"]["origin"]
        == '<a href="umaron">Umaron</a>'
    )
    assert (
        '<a href="garrett">Garrett von Danamark</a>'
        in nolen_record["articles"]["relationships"]
    )
    assert ObjectId("666f6f2d6261722d71757578") in nolen_record["linked_records"]
    assert ObjectId("611be36d862be82b4a41ee68") in nolen_record["linked_records"]

    # don't link to own page
    assert nolen_record["articles"]["description"].find("Nolen") == 0
    assert ObjectId("0123456789ab0123456789ab") not in nolen_record["linked_records"]
