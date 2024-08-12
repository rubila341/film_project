class FilmSearcher:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def search_by_keyword(self, keyword, limit):
        self.logger.log_query(keyword)  # Логируем запрос
        return self.db.search_all_tables_by_keyword(keyword, limit)

    def search_by_genre_and_year(self, genre, year, limit):
        query = f"Жанр: {genre}, Год: {year}"  # Формируем строку запроса для логирования
        self.logger.log_query(query)  # Логируем запрос
        return self.db.search_by_genre_and_year(genre, year, limit)

    def get_all_genres(self):
        return self.db.get_all_genres()

    def get_popular_queries(self):
        return self.logger.get_popular_queries()
