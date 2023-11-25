import os

from dotenv import load_dotenv
from mysql.connector import connect


# Load environment variables from .env file
load_dotenv()


def get_database_connection():
    """Connects to the database using the provided host, user, and password."""
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "wildbase")
    )


def create_database_table():
    """Creates a database & table if they doesn't exist and clears the table."""
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS wildbase")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wildbase.parsertable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255),
            amount INT,
            avg_price FLOAT,
            search_count INT
        )
    """)
    cursor.execute("TRUNCATE TABLE wildbase.parsertable")
    connection.commit()  # Confirm changes


def insert_data_into_table(category, amount, avg_price, search_count):
    """Inserts data into a table in the database.
    :param: category (str) - The chosen category.
            amount (int) - The amount of goods in the category.
            avg_price (float) - The average price of goods in the category.
            search_count (int) - The search count of all related categories.
    """
    connection = get_database_connection()
    cursor = connection.cursor()
    # Convert empty strings to 0 to avoid MySQL errors
    amount = 0 if amount == "" else amount
    search_count = 0 if search_count == "" else search_count

    query = "INSERT INTO wildbase.parsertable (category, amount, avg_price, search_count) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (category, amount, avg_price, search_count))
    connection.commit()  # Confirm changes


def main():  # Close the file if it's open separately since it's only supposed to be used in main.py
    pass


if __name__ == '__main__':
    main()
