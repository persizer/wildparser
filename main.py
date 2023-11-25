# import time
import json
import concurrent.futures

import requests

import sql
from build_category_tree import build_tree


MAX_THREADS = 15
failed_category_list = []
category_list = []

def get_categories():
    """Retrieves all subcategories from the "categories_tree.json" file.
        :return: categories (list) - a list of categories.
    """
    with open("categories_tree.json", encoding="utf-8") as categories_file:
        data = json.load(categories_file)
        categories = [sub_category for subcategories in data.values() for sub_category in subcategories]

    return categories


def find_reachable_categories():
    """Fetches the trending searches for a given category
    to check if it's available to scrape data from.
       :return: category_list (list) - a list of reachable categories.
    """
    categories = get_categories()

    def process_category(category):
        # a for loop is used to avoid skipping categories since the API often returns a blank page
        for _ in range(3):
            url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
            response = requests.get(url, timeout=5).json()
            searches_list = response["data"]["list"]
            if searches_list:
                category_list.append(searches_list[0]["text"])
                print(f"Category reached & added to list: {category}".center(100, "≡") + "\r")
                break
            # time.sleep(1)
            continue

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in categories:
            executor.submit(process_category, category)

    return category_list


def get_search_count(category):
    """Retrieves the search count for a given category.
        :param: category (str) - the category for which the search count is retrieved.
        :return: search_count (int) - the total search count for the given category.
    """
    search_count = 0
    # a for loop is used to avoid skipping categories since the API often returns a blank page
    for _ in range(3):
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url, timeout=5).json()
        if response["data"]["list"]:
            search_count = sum(item["requestCount"] for item in response["data"]["list"])
            break
        # time.sleep(1)
        continue

    return search_count


def get_total_amount(category):
    """Retrieves the total amount of a product from the API for a given category.
        :param: category (str) - the category to search for.
        :return: amount (int) - the total amount of goods for the given category.
    """
    amount = 0
    # a for loop is used to avoid skipping categories since the API often returns a blank page
    for _ in range(3):
        url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=filters&sort=popular&spp=0&suppressSpellcheck=false"
        response = requests.get(url, timeout=5).json()
        if response["data"]["total"]:
            amount = response["data"]["total"]
            break
        # time.sleep(1)
        continue

    return amount


def find_avg_price(category):
    """Calculates the average price of products in a given category.
        :param: category (str) - The category of products to calculate the average price for.
        :return: avg_price (float) - The average price of the products in the category.
    """
    # a for loop is used to avoid skipping categories since the API often returns a blank page
    for _ in range(3):
        url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"
        response = requests.get(url, timeout=5).json()
        if response["data"]["products"]:
            prices = [product["salePriceU"] // 100 for product in response["data"]["products"][:10]]
            avg_price = sum(prices) / len(prices) if prices else 0
            break
        # time.sleep(1)
        continue

    return avg_price


def search_categories(category):
    """Performs analysis on categories:
        finds the average price, total amount and search count of products in the category.
        :param: category (str) - The category to search for.
    """
    try:
        avg_price = find_avg_price(category)
        amount = get_total_amount(category)
        search_count = get_search_count(category)
        sql.insert_data_into_table(avg_price=avg_price, amount=amount, category=category, search_count=search_count)
        print(f"[{category}] Analysis complete!".center(100, "≡") + "\r")
    except ValueError:
        failed_category_list.append(category)


def repeat_failed_categories():
    """Repeats the analysis of failed categories in case of an error."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in failed_category_list:
            index = failed_category_list.index(category)
            try:
                executor.submit(search_categories, category)
                failed_category_list.pop(failed_category_list.index(category))
            except ValueError:
                failed_category_list.append(failed_category_list.pop(index))


def start_parsing():
    """This function is called by running the script.
    It is responsible for starting the parsing process.
    Creates a database table and uses threading to perform analysis on each available category.
    """
    sql.create_database_table()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in category_list:
            try:
                executor.submit(search_categories, category)
            except ValueError:
                pass


if __name__ == '__main__':
    build_tree()
    category_list = find_reachable_categories()
    start_parsing()

    # account for API always returning a blank page for some categories
    while len(failed_category_list) >= 50:
        repeat_failed_categories()

    print("\n" + """

All reachable categories have been analyzed.

""".center(100, "≡") + "\n")
    # Likely that the API returned an empty page
    print("Categories that could not be analyzed due to errors:".center(100, "≡")
          + f"\n{failed_category_list}")
