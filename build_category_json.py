import json


category_file = open('categories.json', encoding='utf-8')
acceptable_categories = ['Электроника', 'Ноутбуки и компьютеры', 'Смартфоны и аксессуары', 'Бытовая техника']
category_json = [item for item in json.load(category_file)['data'] if item['parentName'] in acceptable_categories]


data = {
    "data": category_json,
    "error": False,
    "errorText": "",
    "additionalErrors": None
}
with open('chosen_categories.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)
