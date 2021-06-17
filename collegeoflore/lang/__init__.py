import typing
import os
import yaml


def translate(mapping: dict, key: str) -> typing.Optional[str]:
    print(mapping)
    print(key)
    return mapping.get(key)


def load_locale() -> dict:
    locales = {}
    for root, _, files in os.walk(os.path.dirname(__file__), topdown=False):
        for filename in files:
            name, ext = filename.split('.', 1)
            if ext == 'yml' or ext == "yaml":
                try:
                    with open(os.path.join(root, filename), "r") as ymlfile:
                        locales[name] = yaml.load(ymlfile, Loader=yaml.Loader)
                except FileNotFoundError:
                    print("could not find locale file to load")

    return locales
