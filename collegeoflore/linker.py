import os
from posixpath import dirname


BASE_PATH = os.path.dirname(__file__)
LORE_FOLDER_NAME = "lore"
ALLOWED_DIRS = ["item", "location", "organization", "person"]

# temp func only works for local "lore folder now"
# TODO make this a mongo request


def get_all_articles_dict() -> dict:
    articles = {}
    for root, _, files in os.walk(os.path.join(BASE_PATH, LORE_FOLDER_NAME), topdown=False):
        for name in files:
            try:
                article_category = next(
                    dir_name for dir_name in ALLOWED_DIRS if dir_name in root)
            except StopIteration:
                pass

            article_name = os.path.splitext(name)[0]
            article_path = os.path.join(article_category, article_name)

            print(article_name)
            print(article_path)

            articles.update({article_name: article_path})

    return articles
