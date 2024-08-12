# db.py
import mysql.connector


class SakilaDB:
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Ошибка подключения к базе данных: {err}")
            raise

    def get_all_genres(self):
        query = "SELECT name FROM category"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def search_by_keyword(self, keyword, limit=10):
        query = ("SELECT title, release_year, description FROM film "
                 "WHERE MATCH(title, description) AGAINST(%s IN BOOLEAN MODE) LIMIT %s")
        self.cursor.execute(query, (keyword, limit))
        return self.cursor.fetchall()

    def search_by_genre_and_year(self, genre=None, year=None, limit=10):
        query = """
        SELECT f.title, f.release_year, f.description FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE (%s IS NULL OR LOWER(c.name) = LOWER(%s))
        AND (%s IS NULL OR f.release_year = %s)
        LIMIT %s
        """
        params = (genre, genre, year, year, limit)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_all_tables_by_keyword(self, keyword, limit=10):
        query = """
        (SELECT 'Film' AS source, title AS title, release_year, description
         FROM film
         WHERE title LIKE %s OR description LIKE %s
         LIMIT %s)
        UNION ALL
        (SELECT 'Actor' AS source, CONCAT(first_name, ' ', last_name) AS title, NULL AS release_year, NULL AS description
         FROM actor
         WHERE first_name LIKE %s OR last_name LIKE %s
         LIMIT %s)
        """
        self.cursor.execute(query, (f'%{keyword}%', f'%{keyword}%', limit, f'%{keyword}%', f'%{keyword}%', limit))
        return self.cursor.fetchall()

    def execute_query(self, query, params=None):
        """ Выполняет произвольный SQL-запрос и возвращает результат. """
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()


class QueryLogger:
    def __init__(self, host, user, password, database):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.connection.cursor()
            self.create_table_if_not_exists()
        except mysql.connector.Error as err:
            print(f"Ошибка подключения к базе данных: {err}")
            raise

    def create_table_if_not_exists(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS query_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query TEXT NOT NULL,
            count INT DEFAULT 1,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def log_query(self, query):
        self.cursor.execute("""
            INSERT INTO query_log (query)
            VALUES (%s)
            ON DUPLICATE KEY UPDATE count = count + 1
        """, (query,))
        self.connection.commit()

    def get_popular_queries(self):
        query = "SELECT query, count FROM query_log ORDER BY count DESC LIMIT 10"
        self.cursor.execute(query)
        return self.cursor.fetchall()
