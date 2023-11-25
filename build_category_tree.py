import json

import requests

URL = "https://static-basket-01.wb.ru/vol0/data/subject-base.json"


def build_tree():
    response_json = requests.get(URL, timeout=5).json()  # Fetch from API
    tree = {}
    for obj in response_json:
        main_category = obj["name"]
        sub_categories = [child["name"] for child in obj["childs"]]
        tree[main_category] = sub_categories  # Match main category with subcategories

    with open('categories_tree.json', 'w', encoding='utf-8') as outfile:  # Output to file
        json.dump(tree, fp=outfile, ensure_ascii=False, indent=4)
