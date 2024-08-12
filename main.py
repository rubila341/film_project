import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pytube import Search
from db import SakilaDB, QueryLogger


class ModernMovieSearchApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приложение для поиска фильмов")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2e2e2e; color: #ffffff;")

        # Инициализация базы данных и логгера
        self.db = SakilaDB(host='ich-db.ccegls0svc9m.eu-central-1.rds.amazonaws.com',
                           user='ich1',
                           password='password',
                           database='sakila')
        self.logger = QueryLogger(host='mysql.itcareerhub.de',
                                  user='ich1',
                                  password='ich1_password_ilovedbs',
                                  database='310524ptm_rubila341')

        # Создание главного макета
        self.layout = QVBoxLayout(self)

        # Создание тулбара
        self.create_tool_bar()

        # Создание стека виджетов для разных экранов
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Создание страниц
        self.create_search_by_keyword_page()
        self.create_search_by_genre_and_year_page()
        self.create_popular_queries_page()
        self.create_search_trailers_page()

        # Установка начальной страницы
        self.stacked_widget.setCurrentIndex(0)

        # Добавление кнопки закрытия окна
        self.create_close_button()

    def create_tool_bar(self):
        tool_bar = QtWidgets.QToolBar()
        tool_bar.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.layout.addWidget(tool_bar)

        # Создание кнопки фильтров
        filter_button = QtWidgets.QPushButton("Фильтры")
        filter_button.setStyleSheet(
            "background-color: #007bff; color: white; border-radius: 10px; padding: 15px; font-size: 18px; font-weight: bold;")
        filter_button.setFixedHeight(60)
        filter_button.setFixedWidth(200)
        filter_button.clicked.connect(self.show_filter_menu)

        # Добавление кнопки в тулбар
        tool_bar.addWidget(filter_button)

    def create_close_button(self):
        # Виджет для кнопки закрытия
        close_widget = QtWidgets.QWidget()
        close_layout = QHBoxLayout(close_widget)
        close_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        # Кнопка закрытия окна
        close_button = QtWidgets.QPushButton("X")
        close_button.setStyleSheet(
            "background-color: #ff4d4d; color: white; border-radius: 15px; padding: 10px; font-size: 18px;")
        close_button.clicked.connect(self.close)  # Закрытие окна
        close_button.setFixedSize(30, 30)

        close_layout.addWidget(close_button)
        self.layout.addWidget(close_widget,
                              alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignRight)

    def show_filter_menu(self):
        # Создание и отображение выпадающего меню для выбора фильтров
        menu = QtWidgets.QMenu(self)

        search_by_keyword_action = menu.addAction("Поиск по ключевому слову")
        search_by_keyword_action.triggered.connect(self.show_search_by_keyword_page)

        search_by_genre_action = menu.addAction("Поиск по жанру и году")
        search_by_genre_action.triggered.connect(self.show_search_by_genre_and_year_page)

        popular_queries_action = menu.addAction("Популярные запросы")
        popular_queries_action.triggered.connect(self.show_popular_queries_page)

        search_trailers_action = menu.addAction("Поиск трейлеров")
        search_trailers_action.triggered.connect(self.show_search_trailers_page)

        menu.exec(QtGui.QCursor.pos())  # Показываем меню по позиции курсора

    def create_search_by_keyword_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)  # Изменено на QVBoxLayout для вертикального размещения

        form_layout = QtWidgets.QFormLayout()
        self.keyword_entry = QtWidgets.QLineEdit()
        self.keyword_entry.setPlaceholderText("Введите ключевое слово")
        self.keyword_entry.setStyleSheet("background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")

        self.limit_entry = QtWidgets.QLineEdit()
        self.limit_entry.setPlaceholderText("Количество (по умолчанию 10)")
        self.limit_entry.setStyleSheet("background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")
        self.limit_entry.setText("10")

        search_button = QtWidgets.QPushButton("Поиск")
        search_button.setStyleSheet(
            "background-color: #007bff; color: white; border-radius: 10px; padding: 15px; font-size: 16px;")
        search_button.clicked.connect(self.search_by_keyword)

        form_layout.addRow("Ключевое слово:", self.keyword_entry)
        form_layout.addRow("Количество:", self.limit_entry)
        form_layout.addWidget(search_button)

        layout.addLayout(form_layout)

        # Добавляем отступ для лучшего визуального восприятия
        spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Добавляем виджет таблицы для отображения результатов
        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Название", "Год выхода", "Описание"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)

        self.stacked_widget.addWidget(page)

    def create_search_by_genre_and_year_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)  # Изменено на QVBoxLayout для вертикального размещения

        form_layout = QtWidgets.QFormLayout()
        self.genre_entry = QtWidgets.QLineEdit()
        self.genre_entry.setPlaceholderText("Введите жанр")
        self.genre_entry.setStyleSheet("background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")

        self.year_entry = QtWidgets.QLineEdit()
        self.year_entry.setPlaceholderText("Введите год")
        self.year_entry.setStyleSheet("background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")

        self.limit_entry_genre_year = QtWidgets.QLineEdit()
        self.limit_entry_genre_year.setPlaceholderText("Количество (по умолчанию 10)")
        self.limit_entry_genre_year.setStyleSheet(
            "background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")
        self.limit_entry_genre_year.setText("10")

        search_button = QtWidgets.QPushButton("Поиск")
        search_button.setStyleSheet(
            "background-color: #007bff; color: white; border-radius: 10px; padding: 15px; font-size: 16px;")
        search_button.clicked.connect(self.search_by_genre_and_year)

        form_layout.addRow("Жанр:", self.genre_entry)
        form_layout.addRow("Год:", self.year_entry)
        form_layout.addRow("Количество:", self.limit_entry_genre_year)
        form_layout.addWidget(search_button)

        layout.addLayout(form_layout)

        # Добавляем отступ для лучшего визуального восприятия
        spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Добавляем виджет таблицы для отображения результатов
        self.results_table_genre_year = QtWidgets.QTableWidget()
        self.results_table_genre_year.setColumnCount(3)
        self.results_table_genre_year.setHorizontalHeaderLabels(["Название", "Год выхода", "Описание"])
        self.results_table_genre_year.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table_genre_year)

        self.stacked_widget.addWidget(page)

    def create_popular_queries_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)  # Изменено на QVBoxLayout для вертикального размещения

        self.popular_queries_table = QtWidgets.QTableWidget()
        self.popular_queries_table.setColumnCount(2)
        self.popular_queries_table.setHorizontalHeaderLabels(["Запрос", "Количество"])
        self.popular_queries_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.popular_queries_table)

        self.stacked_widget.addWidget(page)

    def create_search_trailers_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)

        form_layout = QtWidgets.QFormLayout()
        self.trailer_title_entry = QtWidgets.QLineEdit()
        self.trailer_title_entry.setPlaceholderText("Введите название фильма")
        self.trailer_title_entry.setStyleSheet(
            "background-color: #555555; color: #ffffff; border-radius: 5px; padding: 5px;")

        search_button = QtWidgets.QPushButton("Поиск трейлеров")
        search_button.setStyleSheet(
            "background-color: #007bff; color: white; border-radius: 10px; padding: 15px; font-size: 16px;")
        search_button.clicked.connect(self.search_trailers)

        form_layout.addRow("Название фильма:", self.trailer_title_entry)
        form_layout.addWidget(search_button)

        layout.addLayout(form_layout)

        # Добавляем отступ для лучшего визуального восприятия
        spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

        # Виджет для отображения видео
        self.video_layout = QVBoxLayout()
        layout.addLayout(self.video_layout)

        self.stacked_widget.addWidget(page)

    def show_search_by_keyword_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_search_by_genre_and_year_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_popular_queries_page(self):
        self.update_popular_queries()
        self.stacked_widget.setCurrentIndex(2)

    def show_search_trailers_page(self):
        self.stacked_widget.setCurrentIndex(3)

    def search_by_keyword(self):
        keyword = self.keyword_entry.text()
        limit = self.limit_entry.text()

        if not keyword:
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода", "Необходимо указать ключевое слово.")
            return

        if not limit.isdigit():
            limit = 10
        else:
            limit = int(limit)

        try:
            results = self.db.search_all_tables_by_keyword(keyword, limit)
            self.display_results(results, page=0)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {e}")

    def search_by_genre_and_year(self):
        genre = self.genre_entry.text() or None
        year = self.year_entry.text() or None
        limit = self.limit_entry_genre_year.text()

        if not limit.isdigit():
            limit = 10
        else:
            limit = int(limit)

        if not (genre or year):
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода",
                                          "Необходимо указать хотя бы один фильтр (жанр или год).")
            return

        try:
            films = self.db.search_by_genre_and_year(genre, year, limit)
            self.display_results(films, page=1)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка выполнения запроса: {e}")

    def update_popular_queries(self):
        try:
            popular_queries = self.logger.get_popular_queries()
            self.popular_queries_table.setRowCount(len(popular_queries))
            for row, query in enumerate(popular_queries):
                self.popular_queries_table.setItem(row, 0, QtWidgets.QTableWidgetItem(query[0]))
                self.popular_queries_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(query[1])))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка получения популярных запросов: {e}")

    def search_trailers(self):
        movie_title = self.trailer_title_entry.text()

        if not movie_title:
            QtWidgets.QMessageBox.warning(self, "Ошибка ввода", "Необходимо указать название фильма.")
            return

        try:
            query = f"{movie_title} трейлер"
            search = Search(query)
            results = search.results[:1]  # Получаем только первый результат

            # Очистка предыдущих видео
            for i in reversed(range(self.video_layout.count())):
                widget_to_remove = self.video_layout.itemAt(i).widget()
                self.video_layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)

            if results:
                video_url = results[0].watch_url
                web_view = QWebEngineView()
                web_view.setUrl(QtCore.QUrl(video_url))
                self.video_layout.addWidget(web_view)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка поиска трейлеров: {e}")

    def display_results(self, results, page):
        if page == 0:
            self.results_table.setRowCount(len(results))
            for row, result in enumerate(results):
                self.results_table.setItem(row, 0, QtWidgets.QTableWidgetItem(result['title']))
                self.results_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(result['release_year'])))
                self.results_table.setItem(row, 2, QtWidgets.QTableWidgetItem(result['description']))
        elif page == 1:
            self.results_table_genre_year.setRowCount(len(results))
            for row, result in enumerate(results):
                self.results_table_genre_year.setItem(row, 0, QtWidgets.QTableWidgetItem(result['title']))
                self.results_table_genre_year.setItem(row, 1, QtWidgets.QTableWidgetItem(str(result['release_year'])))
                self.results_table_genre_year.setItem(row, 2, QtWidgets.QTableWidgetItem(result['description']))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ModernMovieSearchApp()
    window.show()
    sys.exit(app.exec())
