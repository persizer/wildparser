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
            avg_price INT
        )
    """)
    cursor.execute("TRUNCATE TABLE wildbase.parsertable")
    connection.commit()


def insert_data_into_table(category, amount, avg_price):
    connection = connect(host="localhost", user="root", password="rE*=|||123", database="wildbase")
    cursor = connection.cursor()
    amount = 0 if amount == "" else amount
    query = "INSERT INTO wildbase.parsertable(category, amount, avg_price) VALUES (%s, %s, %s)"
    cursor.execute(query, (category, amount, avg_price))
    connection.commit()


def main():
    pass


if __name__ == '__main__':
    main()
