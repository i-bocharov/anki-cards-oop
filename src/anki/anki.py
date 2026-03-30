from typing import Dict, Iterator, Optional, Tuple
import random
import time


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
        # Защита от изменяемого объекта по умолчанию.
        if words is None:
            words = {}

        # Валидация и нормализация через защищённый метод.
        # Устраняет дублирование кода с сеттером.
        self._words: Dict[str, str] = self._normalize_dict(words)

        # Начата ли сессия тренировки до первой ошибки.
        self._session_active = False
        # Время начала тренировки.
        self._session_start_time = 0.0
        # Количество правильных ответов.
        self._session_user_score = 0
        # Последнее выданное слово в сессии.
        self._last_session_word: Optional[str] = None

        # Информация о последней тренировке.
        self.last_session_stats = {
            "correct_answers": 0,
            "total_time": 0.0,
        }

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

    def _normalize_dict(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Валидирует и нормализует весь словарь слов.

        Защищённый метод для устранения дублирования кода в __init__ и
        сеттере. Гарантирует, что внутренний словарь содержит только
        нормализованные строки.

        Args:
            data (Dict[str, str]): Словарь для нормализации.

        Returns:
            Dict[str, str]: Новый словарь с нормализованными ключами и
                значениями.

        Raises:
            ValueError: Если входные данные не словарь или содержат
                нестроковые значения.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f'Параметр words должен быть словарём, '
                f'получено: {type(data).__name__}'
            )

        normalized: Dict[str, str] = {}
        for key, value in data.items():
            # normalize_word выбросит ValueError, если ключ или значение не
            # строка.
            norm_key = self.normalize_word(key)
            norm_value = self.normalize_word(value)
            normalized[norm_key] = norm_value

        return normalized

    @property
    def words(self) -> Dict[str, str]:
        """
        Возвращает копию словаря слов.

        Геттер возвращает копию, чтобы предотвратить модификацию
        внутреннего состояния объекта (_words) извне.

        Returns:
            Dict[str, str]: Копия словаря пар слово-перевод.
        """
        # Создаем поверхностную копию. Так как значения - неизменяемые строки,
        # глубокое копирование не требуется, что улучшает производительность.
        return {**self._words}

    @words.setter
    def words(self, value: Dict[str, str]) -> None:
        """
        Устанавливает новый словарь слов с валидацией и нормализацией.

        Сеттер использует _normalize_dict для обеспечения целостности данных.

        Args:
            value (Dict[str, str]): Новый словарь пар слово-перевод.

        Raises:
            ValueError: Если переданные данные не проходят валидацию.
        """
        # Защита от изменения слов во время активной сессии.
        if self._session_active:
            raise ValueError(
                'Нельзя менять слова во время активной тренировки.'
            )

        # Делегируем валидацию и нормализацию защищённому методу
        self._words = self._normalize_dict(value)

    def start_session(self):
        """Начинает новую тренировочную сессию."""
        if self._session_active:
            raise RuntimeError(
                'Нельзя начать тренировку, если она уже начата.'
            )

        self._session_active = True
        self._session_start_time = time.time()
        self._session_user_score = 0
        self._last_session_word = None

    def end_session(self):
        """Завершает текущую тренировочную сессию."""
        if not self._session_active:
            raise RuntimeError('Нельзя завершить неактивную сессию.')

        # Вычисляем время сессии. Гарантируем минимальное значение для
        # корректной статистики.
        session_time = max(time.time() - self._session_start_time, 0.001)

        self.last_session_stats = {
            "correct_answers": self._session_user_score,
            "total_time": session_time
        }

        # Сбрасываем состояние.
        self._session_active = False
        self._session_user_score = 0
        self._session_start_time = 0.0
        self._last_session_word = None

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

        word = random.choice(list(self._words.keys()))

        # Сохраняем последнее выданное слово для активной сессии.
        if self._session_active:
            self._last_session_word = word

        return word

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

        # Проверка для активной сессии: слово должно совпадать с последним
        # выданным.
        if self._session_active:
            if self._last_session_word is None:
                self.end_session()
                raise ValueError(
                    'Сначала получите слово через get_random_word().'
                )

            if normalized_word != self._last_session_word:
                self.end_session()
                raise ValueError(
                    'Работаем только с последним выданным словом.'
                )

        is_correct = self._words[normalized_word] == normalized_translation

        # Логика сессии: правильный ответ увеличивает счёт, неправильный
        # завершает сессию.
        if self._session_active:
            if is_correct:
                self._session_user_score += 1
                # Сбрасываем последнее слово после успешной проверки.
                self._last_session_word = None
            else:
                self.end_session()

        return is_correct

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
