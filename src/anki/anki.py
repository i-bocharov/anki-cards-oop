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

    @staticmethod
    def normalize_word(word: str) -> str:
        """
        Нормализует строку: удаляет пробелы и приводит к нижнему регистру.
        Выбрасывает ValueError, если аргумент не строка.
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
        """
        # Валидация и нормализация делегирована статическому методу.
        # Если типы неверные, ошибка возникнет здесь автоматически.
        norm_word = self.normalize_word(word)
        norm_translation = self.normalize_word(translation)

        self._words[norm_word] = norm_translation

    def get_words(self) -> Dict[str, str]:
        """
        Возвращает глубокую копию словаря для безопасного использования.
        Изменения копии не повлияют на внуреннее поведение класса.
        """
        return deepcopy(self._words)
