from abc import ABC, abstractmethod  # подключаем инструменты для создания абстрактных классов

import pandas  # пакет для работы с датасетами

"""
    В данном модуле реализуются классы обработчиков для 
    применения алгоритма обработки (csv).
"""

# Column names
last_year = '2020'
year_before_last = '2019'
Difference = 'Difference'
country = 'country'


class DataProcessor(ABC):
    """ Родительский класс для обработчиков файлов """

    def __init__(self, datasource: str):
        # общие атрибуты для классов обработчиков данных
        self._datasource = datasource  # путь к источнику данных
        self._dataset = None  # входной набор данных
        self.result = None  # выходной набор данных (результат обработки)

    # Все методы, помеченные декоратором @abstractmethod, ОБЯЗАТЕЛЬНЫ для переопределения в классах-потомках
    @abstractmethod
    def read(self) -> bool:
        """ Метод, инициализирующий источник данных """
        pass

    def run(self) -> None:
        """ Метод, запускающий обработку данных """
        # Создаем пустой DataFrame в атрибуте класса для сохранения результатов обработки
        self.result = pandas.DataFrame()
        self._dataset[Difference] = (self._dataset[last_year] - self._dataset[year_before_last]) / self._dataset[
            year_before_last] * 100
        self._dataset = self.sort_data_by_col(self._dataset, Difference, False)
        self.result[country] = self._dataset[country]
        self.result[year_before_last] = self._dataset[year_before_last]
        self.result[last_year] = self._dataset[last_year]
        self.result[Difference] = self._dataset[Difference]

    """
        Ниже представлены примеры различных методов для обработки набора данных.
        Основные методы для работы с объектом DataFrame см. здесь: 
        https://pandas.pydata.org/docs/reference/general_functions.html

        ВАЖНО! Следует логически разделять методы обработки, например, отдельный метод для сортировки, 
        отдельный метод для удаления "пустот" в датасете (очистка) и т.д. Это позволит гибко применять необходимые
        методы при переопределении метода run для того или иного типа обработчика.

        Также обратите внимание на то, что названия методов и функций для обработки должны быть ОСМЫСЛЕННЫМИ, т.е. 
        предоставлять информацию о том, что конкретно выполняет данный метод или функция.
    """

    def sort_data_by_col(self, df: pandas.DataFrame, colname: str, asc: bool) -> pandas.DataFrame:
        """
            Метод sort_data_by_col просто сортирует входной датасет по наименованию
            заданной колонки (аргумент colname) и устанвливает тип сортировки:
            ascending = True - по возрастанию, ascending = False - по убыванию
        """
        return df.sort_values(by=[colname], ascending=asc)

    @abstractmethod
    def print_result(self) -> None:
        """ Абстрактный метод для вывода результата на экран """
        pass


class CsvDataProcessor(DataProcessor):
    """ Реализация класса-обработчика csv-файлов """

    def __init__(self, datasource: str):
        # Переопределяем конструктор родительского класса
        DataProcessor.__init__(self,
                               datasource)  # инициализируем конструктор родительского класса для получения общих атрибутов
        self.separators = [';', ',', '|']  # список допустимых разделителей

    """
        Переопределяем метод инициализации источника данных.
        Т.к. данный класс предназначен для чтения CSV-файлов, то используем метод read_csv
        из библиотеки pandas
    """

    def read(self):
        try:
            # Пытаемся преобразовать данные файла в pandas.DataFrame, используя различные разделители
            for separator in self.separators:
                self._dataset = pandas.read_csv(self._datasource, sep=separator, on_bad_lines='skip')
                self._dataset = self._dataset.fillna('0')
                # Читаем имена колонок из файла данных
                col_names = self._dataset.columns
                # Если количество считанных колонок > 1 возвращаем True
                if len(col_names) > 1:
                    self._dataset = self._dataset[
                        (self._dataset[last_year] != '0') & (self._dataset[year_before_last] != '0')]

                    self._dataset[last_year] = self._dataset[last_year].replace('.', ',', regex=True)

                    self._dataset[year_before_last] = self._dataset[year_before_last].replace('.', ',', regex=True)

                    print(f'Columns read: {col_names} using separator {separator}')

                    return True
        except Exception as e:
            print(e)
        return False

    def print_result(self):
        print(f'Running CSV-file processor!\n', self.result.head())


