from mysql.connector import connect


def create_database_table():
    connection = connect(host="localhost", user="root", password="rE*=|||123", database="wildbase")
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS wildbase")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wildbase.parsertable (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255),
            amount INT,
            avg_price INT,
            search_count INT
        )
    """)
    cursor.execute("TRUNCATE TABLE wildbase.parsertable")
    connection.commit()


def insert_data_into_table(category, amount, avg_price, search_count):
    connection = connect(host="localhost", user="root", password="rE*=|||123", database="wildbase")
    cursor = connection.cursor()
    amount = 0 if amount == "" else amount
    search_count = 0 if search_count == "" else search_count
    query = "INSERT INTO wildbase.parsertable(category, amount, avg_price, search_count) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (category, amount, avg_price, search_count))
    connection.commit()


def main():
    pass


if __name__ == '__main__':
    main()
