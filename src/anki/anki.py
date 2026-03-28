from typing import Dict, Iterator, Optional, Tuple
from copy import deepcopy
import random


class Anki:
    """
    Класс для управления коллекцией слов для изучения.

    Хранит пары «слово-перевод», обеспечивает нормализацию данных
    и валидацию типов при добавлении новых записей.
    Реализует протоколы итерируемого объекта и вычисления длины.
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
        normalized_words: Dict[str, str] = {}

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

    def __str__(self) -> str:
        """
        Возвращает человеко-читаемое представление объекта.

        Returns:
            str: Строка с информацией о количестве слов в коллекции.
        """
        return f'Количество слов в коллекции Anki: {len(self._words)}'

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        """
        Возвращает итератор по парам слово-перевод.

        Returns:
            Iterator[Tuple[str, str]]: Итератор по кортежам (слово, перевод).
        """
        return iter(self._words.items())

    def __len__(self) -> int:
        """
        Возвращает количество слов в коллекции.

        Returns:
            int: Количество пар слово-перевод в коллекции.
        """
        return len(self._words)

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

    def get_random_word(self) -> str:
        """
        Возвращает случайное слово из коллекции для изучения.

        Returns:
            str: Случайное слово из словаря (нормализованное).

        Raises:
            ValueError: Если коллекция слов пуста.
        """
        if not self._words:
            raise ValueError(
                'Коллекция слов пуста. Добавьте слова.'
            )

        return random.choice(list(self._words.keys()))

    def get_random_word_pair(self) -> Tuple[str, str]:
        """
        Возвращает случайную пару (слово, перевод) для игрового режима.

        Returns:
            Tuple[str, str]: Кортеж из слова и его перевода.

        Raises:
            ValueError: Если коллекция слов пуста.
        """
        if not self._words:
            raise ValueError(
                'Коллекция слов пуста. Добавьте слова перед началом игры.'
            )

        return random.choice(list(self._words.items()))

    def check_translation(self, word: str, translation: str) -> bool:
        """
        Проверяет корректность перевода для указанного слова.

        Args:
            word (str): Слово для проверки.
            translation (str): Перевод для проверки.

        Returns:
            bool: True, если перевод корректен, иначе False.

        Raises:
            ValueError: Если слово отсутствует в коллекции или не строка.
        """
        if not isinstance(word, str):
            raise ValueError(
                f'Параметр word должен быть строкой, '
                f'получено: {type(word).__name__}'
            )

        if not isinstance(translation, str):
            raise ValueError(
                f'Параметр translation должен быть строкой, '
                f'получено: {type(translation).__name__}'
            )

        normalized_word = self.normalize_word(word)
        normalized_translation = self.normalize_word(translation)

        if normalized_word not in self._words:
            raise ValueError(
                f'Слово "{normalized_word}" отсутствует в коллекции.'
            )

        return self._words[normalized_word] == normalized_translation

    def get_translation(self, word: str) -> str:
        """
        Возвращает перевод для указанного слова.

        Args:
            word (str): Слово для получения перевода.

        Returns:
            str: Перевод слова.

        Raises:
            ValueError: Если слово отсутствует в коллекции или не строка.
        """
        if not isinstance(word, str):
            raise ValueError(
                f'Параметр word должен быть строкой, '
                f'получено: {type(word).__name__}'
            )

        normalized_word = self.normalize_word(word)

        if normalized_word not in self._words:
            raise ValueError(
                f'Слово "{normalized_word}" отсутствует в коллекции.'
            )

        return self._words[normalized_word]
