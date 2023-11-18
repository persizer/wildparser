import json
import requests
import concurrent.futures
import sql


MAX_THREADS = 50
failed_category_list = []


def get_categories():
    
    """
    Retrieves all subcategories from the "categories_struct.json" file.
    Parameters:
        None
    Returns:
        categories (list): A list of categories.
    """
    
    with open("categories_struct.json", encoding="utf-8") as categories_file:
        data = json.load(categories_file)
        categories = [sub_category for subcategories in data.values() for sub_category in subcategories]
        
    return categories


def find_reachable_categories():
    
    """
    Fetches the trending searches for a given category to check if it's available to scrape data from.
    Parameters:
        None
    Returns:
       category_list (list): A list of reachable categories.
    """
    
    global category_list
    category_list = []
   
    def process_category(category):
        url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
        response = requests.get(url).json()
        searches_list = response["data"]["list"]
        
        for _ in range(3):
            if searches_list:
                category_list.append(searches_list[0]["text"])
                print(f"Category reached & added to list: {category}".center(100, "≡"))
                break
            else: 
                continue
        
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_category, get_categories())
    
    return category_list


def get_search_count(category):
    
    """
    Retrieves the search count for a given category.
    Parameters:
        category (str): The category for which the search count is retrieved.
    Returns:
        search_count (int): The total search count for the given category.
    """
    
    url = f"https://trending-searches.wb.ru/api?itemsPerPage=1000000&offset=0&period=week&query={category}"
    response = requests.get(url).json()
    
    for _ in range(3):
        if response["data"]["list"]:
            search_count = sum(item["requestCount"] for item in response["data"]["list"])
            break
        else:
            continue
        
    return search_count


def get_total_amount(category):
    
    """
    Retrieves the total amount of a product from the API for a given category.
    Parameters:
        category (str): The category to search for.
    Returns:
        amount (int): The total amount for the given category of product retrieved from the API.
    """
    
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=filters&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    
    for _ in range(3):
        if response["data"]["total"]:
            break
        else:
            continue
        
    amount = response["data"]["total"]
    return amount 



def find_avg_price(category):
    
    """
    Calculates the average price of products in a given category.
    Args:
        category (str): The category of products to calculate the average price for.
    Returns:
        avg_price (float): The average price of the products in the category. If no products are found, returns 0.
    """
    
    url = f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0&query={category}&reg=0&regions=80,64,83,4,38,33,70,68,69,86,75,30,40,48,1,66,31,22,71&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false"
    response = requests.get(url).json()
    
    for _ in range(3):
        if response["data"]["products"]:
            prices = [product["salePriceU"] // 100 for product in response["data"]["products"][:10]]
            avg_price = sum(prices) / len(prices) if prices else 0
            break
        else:
            continue
        
    return avg_price 


def search_categories(category):
    
    """
    Searches for categories and performs analysis on them:
        - Finds the average price of products in the category
        - Finds the total amount of products in the category
        - Finds the search count of products in the category
    Parameters:
        category (str): The category to search for.
    Returns:
        None
    """
    
    try:
        avg_price = find_avg_price(category)
        amount = get_total_amount(category)
        search_count = get_search_count(category)
        sql.insert_data_into_table(avg_price=avg_price, amount=amount, category=category, search_count=search_count)
        print(f"[{category}] Analysis complete!".center(100, "≡"))
    except Exception as e:
        failed_category_list.append(category)
        error_message = f"[{category}] Error. {e}"
        print(error_message.center(100, "×"))


def repeat_failed_categories():
    
    """
    Repeats the analysis of failed categories in case of an error.
    Parameters:
        None
    Returns:
        None
    """
    
    global failed_category_list
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in failed_category_list:
            try:
                executor.submit(search_categories, category)
                failed_category_list.pop(failed_category_list.index(category))
            except Exception as e:
                failed_category_list.append(failed_category_list.pop(failed_category_list.index(category)))
                error_message = f"[{category}] Error. {e}"
                print(error_message.center(100, "×"))
                
                
def start_parsing():
    
    """
    This function is called by running the script.
    It is responsible for starting the parsing process.
    Creates a database table and uses threading to perform analysis on each available category.
    Parameters:
        None
    Returns:
        None
    """
    
    sql.create_database_table()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for category in category_list:
            try:
                print(f"Starting search for category: {category}".center(100, "="))
                executor.submit(search_categories, category)
                
            except Exception as e:
                error_message = f"[{category}] Error. {e}"
                print(error_message.center(100, "×"))
        

if __name__ == '__main__':
    category_list = find_reachable_categories()
    start_parsing()
    while len(failed_category_list) > 50:
        repeat_failed_categories()