import json
import requests
from threading import Thread

import sql


def get_categories():
    with open("categories.json", encoding="UTF-8") as categories_file:
        data = json.load(categories_file)["data"]
        sub_categories = [item["sub_category"] for item in data] 
        return sub_categories


def find_reachable_categories():
    categories = get_categories()
    global category_list
    category_list = []
    for category in categories:
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url).json()
        str_list = response["data"]["list"]
        if str_list:
            category_list.append(str_list[0]["text"])
            print(f"Category reachable & appended to list: {category}").center(100, "=")
        else:
            print(f"Empty string list for category: {category}").center(100, "=")
    return category_list


def search_count():
    for category in category_list:
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url).json()
        if response["data"]["list"]:
            search_count = sum(item["requestCount"] for item in response["data"]["list"])
            print(f"Total search count for {category}: {search_count}").center(100, "=")
        else:
            print(f"No data found for {category}").center(100, "=")


def get_total_amount(category):
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=filters&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    return response["data"]["total"]



def find_avg_price(category):
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    prices = [product["salePriceU"] // 100 for product in response["data"]["products"][:10]]
    avg_price = sum(prices) / len(prices)
    return avg_price


threads = 0


def search_categories(category):
    global threads
    try:
        threads += 1
        avg_price = find_avg_price(category)
        amount = get_total_amount(category)
        sql.insert_data_into_table(avg_price=avg_price, amount=amount, category=category)
        print(f"[{category}] Analysis complete! Threads: {threads}").center(100, "=")
    except Exception as e:
        print(f"[{category}] Error. Threads: {threads}.\n{e}" ).center(100, "=")
    finally:
        threads -= 1


def start_parsing():
    sql.create_database_table()
    for category in category_list:
        try:
            while threads >= 50:
                pass
            print(f"Starting search for category: {category}")
            thread = Thread(target=search_categories, args=(category,))
            thread.start()
        except Exception as e:
            error_message = f"[{category}] Error. Threads: {threads}.\n{e}"
            print(error_message.center(100, "="))
            raise RuntimeError(error_message)


if __name__ == '__main__':
    category_list = find_reachable_categories()
    start_parsing()