import json


category_file = open('c.json', 'r+', encoding='utf-8')
category_json = [item for item in json.load(category_file)['data']]
output_category_list = []
output_file = open('categories.json', 'w', encoding='utf-8')


for item in category_json:
    item.pop('isVisible', None)
    item['main_category'] = item.pop('parentName')
    item['sub_category'] = item.pop('objectName')

    if ('для взрослых' in item['main_category']
            or 'для взрослых' in item['sub_category']
            or '18+' in item['sub_category']):
        del item
        continue
    output_category_list.append(item)
    
    
data = {
    "data": output_category_list,
}


json.dump(data, output_file, ensure_ascii=False, indent=4)
category_file.close()
output_file.close()