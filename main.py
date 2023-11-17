import json
import requests
from threading import Thread

import sql


def get_categories():
    with open("chosen_categories.json", encoding="UTF-8") as categories_file:
        return map(lambda x: x["objectName"], json.load(categories_file)["data"])


# def parse_search():
# categories = get_categories()
# for category in categories:
# url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
# json_data = requests.get(url).json()
# print(json_data) if json_data["data"]["list"] else None


def find_usable_categories():
    categories = get_categories()
    for category in categories:
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url).json()
        str_list = response["data"]["list"]
        print(str_list[0]["text"]) if str_list else None


def search_count():
    categories = get_categories()
    for category in categories:
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url).json()
        print(sum([item["requestCount"] for item in response["data"]["list"]])) if response["data"]["list"] else None


def find_avg_price(category):
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    prices = [product["salePriceU"] // 100 for product in response["data"]["products"][:10]]
    return sum(prices) / len(prices)


def get_total_amount(category):
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=filters&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    return response["data"]["total"]


threads = 0


def analyze_category(category):
    global threads
    try:
        threads += 1
        avg_price = find_avg_price(category)
        amount = get_total_amount(category)
        sql.insert_data_into_table(avg_price=avg_price, amount=amount, category=category)
        print(f"[{category}] Анализ завершён!. Потоков: {threads}".center(100, "-"))
    except Exception as e:
        print(f"[{category}] Ошибка. Потоков: {threads}".center(100, "-") + f"\n{e}")
    finally:
        threads -= 1


def start_parse():
    categories = get_categories()
    sql.create_database_table()
    for category in categories:
        try:
            while threads >= 50:
                pass
            thread = Thread(target=analyze_category, args=(category,))
            thread.start()
        except Exception as e:
            print(f"[{category}] Ошибка. Потоков: {threads}".center(100, "-") + f"\n{e}")


if __name__ == '__main__':
    start_parse()
