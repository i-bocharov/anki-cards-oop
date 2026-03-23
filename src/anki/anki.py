from typing import Dict, Optional
from copy import deepcopy


class Anki:
    """
    Класс для управления коллекцией слов для изучения.

    Хранит пары «слово-перевод», обеспечивает нормализацию данных
    и валидацию типов при добавлении новых записей.
    """

    def __init__(self, *, words: Optional[Dict[str, str]] = None):
        """
        Инициализирует коллекцию с валидацией и нормализацией данных.
        Создает защищенный атрибут _words для хранения пар.

        Args:
            words (Optional[Dict[str, str]]): Словарь пар слово-перевод.
                По умолчанию None (создается пустой словарь).
        """
        # Защита от изменяемого объекта по умолчанию
        if words is None:
            words = {}

        # Проверка типа контейнера
        if not isinstance(words, dict):
            raise ValueError(
                f'Параметр words должен быть словарём ,'
                f'получено: {type(words).__name__}'
            )

        # Создаем новый словарь с нормализованными данными.
        normalized_words = {}

        # Валидация типов ключей и значений
        for key, value in words.items():
            # Валидация и нормализация через статический метод
            # Если тип неверный, normalize_word выбросит ValueError.
            norm_key = self.normalize_word(key)
            norm_value = self.normalize_word(value)

            normalized_words[norm_key] = norm_value

        # Присваивание только после успешной валидации
        self._words = normalized_words

    def __contains__(self, word: object) -> bool:
        """
        Проверяет наличие нормализованного слова в коллекции.

        Args:
            word (object): Слово для поиска. Должно быть строкой.

        Returns:
            bool: True, если слово найдено, иначе False.

        Raises:
            ValueError: Если переданный аргумент не является строкой.
        """
        # Явная проверка типа для безопасности.
        # Это предотвращает передачу некорректных данных в normalize_word.
        if not isinstance(word, str):
            raise ValueError(
                f'Аргумент для проверки вхождения должен быть строкой, '
                f'получено: {type(word).__name__}'
            )

        normalized_word = self.normalize_word(word)
        return normalized_word in self._words

    def __str__(self):
        """
        Возвращает человеко-читаемое представление объекта.

        Returns:
            str: Строка с информацией о количестве слов в коллекции.
        """
        return f'Количество слов в коллекции Anki: {len(self._words)}'

    @staticmethod
    def normalize_word(word: str) -> str:
        """
        Нормализует строку: удаляет пробелы и приводит к нижнему регистру.

        Args:
            word (str): Строка для нормализации (слово или перевод).

        Returns:
            str: Нормализованная строка.

        Raises:
            ValueError: Если переданный аргумент не является строкой.
        """
        if not isinstance(word, str):
            raise ValueError(
                'Слово должно быть строкой, '
                f'получено: {type(word).__name__} ({word!r})'
            )

        return word.strip().lower()

    def add_word(self, word: str, translation: str) -> None:
        """
        Добавляет пару слово-перевод в словарь после нормализации.

        Args:
            word (str): Слово для добавления.
            translation (str): Перевод слова.
        """
        # Валидация и нормализация делегирована статическому методу.
        # Если типы неверные, ошибка возникнет здесь автоматически.
        norm_word = self.normalize_word(word)
        norm_translation = self.normalize_word(translation)

        self._words[norm_word] = norm_translation

    def get_words(self) -> Dict[str, str]:
        """
        Возвращает глубокую копию словаря для безопасного использования.

        Returns:
            Dict[str, str]: Глубокая копия словаря пар слово-перевод.
            Изменения копии не повлияют на внуреннее состоние объекта.
        """
        return deepcopy(self._words)
