import random
import time
from collections.abc import Iterator


class TrainingSession:
    """
    Базовый класс для тренировочных сессий.

    Управляет состоянием тренировки: время, счёт, последнее слово.
    Делегирует работу со словарём классу Anki.
    """

    def __init__(self, anki: 'Anki') -> None:
        self.active: bool = True

        self._anki: 'Anki' = anki
        self._start_time: float = time.time()
        self._end_time: float = self._start_time
        self._user_score: int = 0
        self._last_word: str | None = None

    def get_random_word(self) -> str:
        """
        Получает случайное слово из словаря Anki.

        Returns:
            str: Случайное слово для перевода.

        Raises:
            ValueError: Если сессия не активна.
        """
        if not self.active:
            raise ValueError('Сессия не активна. Начните новую тренировку.')

        word = self._anki.get_random_word()

        self._last_word = word

        return word

    def check_translation(self, word: str, translation: str) -> bool:
        """
        Проверяет корректность перевода через Anki.

        Args:
            word (str): Слово для проверки.
            translation (str): Перевод для проверки.

        Returns:
            bool: True, если перевод корректен.

        Raises:
            ValueError: Если сессия не активна.
        """
        if not self.active:
            raise ValueError('Сессия не активна. Начните новую тренировку.')

        # Защита от накрутки: проверяем только последнее полученное слово.
        if self._last_word is None or word != self._last_word:
            raise ValueError('Сначала получите слово через get_random_word().')

        is_correct = self._anki.check_translation(word, translation)

        # Сбрасываем последнее слово после проверки
        # Это предотвращает повторную проверку того же слова
        self._last_word = None

        return is_correct

    def end_session(self) -> None:
        """
        Завершает тренировочную сессию.

        Устанавливает флаг active в False и обновляет время окончания.

        Raises:
            ValueError: Если сессия уже завершена.
        """
        if not self.active:
            raise ValueError('Сессия уже завершена.')

        self.active = False
        self._end_time = time.time()
        self._anki.end_session()

    def get_stat(self) -> dict[str, float | int]:
        """
        Возвращает статистику текущей сессии.

        Returns:
            dict[str, float | int]: Словарь с ключами:
                - correct_answers (int): количество правильных ответов
                - total_time (float): время сессии в секундах
        """
        if self.active:
            total_time = time.time() - self._start_time
        else:
            total_time = self._end_time - self._start_time

        return {'correct_answers': self._user_score, 'total_time': total_time}


class ZeroMistakesTraining(TrainingSession):
    """
    Тренировка до первой ошибки.

    Завершается при первом неправильном ответе.
    """

    def check_translation(self, word: str, translation: str) -> bool:
        """
        Проверяет перевод и завершает сессию при ошибке.

        Args:
            word (str): Слово для проверки.
            translation (str): Перевод для проверки.

        Returns:
            bool: True, если перевод корректен.
        """
        is_correct = super().check_translation(word, translation)

        if is_correct:
            self._user_score += 1
            pass
        else:
            self.end_session()

        return is_correct


class TimeLimitedTraining(TrainingSession):
    """
    Тренировка с ограничением по времени.

    Завершается по истечении заданного лимита времени.
    Позволяет пользователю дать последний ответ без ограничений.
    """

    def __init__(self, anki: 'Anki', time_limit: float = 60.0) -> None:
        """
        Инициализирует тренировку с ограничением по времени.

        Args:
            anki (Anki): Экземпляр игры Anki для работы со словами.
            time_limit (float): Лимит времени в секундах. По умолчанию 60.0.
        """
        super().__init__(anki)
        self._time_limit: float = time_limit

    def _time_remaining(self) -> float:
        """
        Возвращает оставшееся время сессии.

        Returns:
            float: Оставшееся время в секундах.
        """
        elapsed = time.time() - self._start_time
        return max(self._time_limit - elapsed, 0.0)

    def check_translation(self, word: str, translation: str) -> bool:
        """
        Проверяет перевод с учётом ограничения по времени.

        Позволяет пользователю дать последний ответ даже если время истекло.
        Завершает сессию после проверки, если время вышло.

        Args:
            word (str): Слово для проверки.
            translation (str): Перевод для проверки.

        Returns:
            bool: True, если перевод корректен.
        """
        is_correct = super().check_translation(word, translation)

        if is_correct:
            self._user_score += 1
            # Сброс последнего слова уже в базовом классе.
            pass

        # Проверяем, истекло ли время после ответа.
        if self._time_remaining() <= 0:
            self.end_session()

        return is_correct


class Anki:
    """
    Класс для управления коллекцией слов для изучения.

    Хранит пары «слово-перевод», обеспечивает нормализацию данных
    и валидацию типов при добавлении новых записей.
    Реализует протоколы итерируемого объекта и вычисления длины.
    """

    def __init__(self, *, words: dict[str, str] | None = None) -> None:
        """
        Инициализирует коллекцию с валидацией и нормализацией данных.
        Создает защищенный атрибут _words для хранения пар.

        Args:
            words (dict[str, str] | None): Словарь пар слово-перевод.
                По умолчанию None (создается пустой словарь).
        """
        # Защита от изменяемого объекта по умолчанию.
        if words is None:
            words = {}

        # Валидация и нормализация через защищённый метод.
        # Устраняет дублирование кода с сеттером.
        self._words: dict[str, str] = self._normalize_dict(words)

        # Начата ли сессия тренировки до первой ошибки.
        self._session_active: bool = False

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

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """
        Возвращает итератор по парам слово-перевод.

        Returns:
            Iterator[tuple[str, str]]: Итератор по кортежам (слово, перевод).
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
                f'Слово должно быть строкой, получено: {type(word).__name__} ({word!r})'
            )

        return word.strip().lower()

    def _normalize_dict(self, data: dict[str, str]) -> dict[str, str]:
        """
        Валидирует и нормализует весь словарь слов.

        Защищённый метод для устранения дублирования кода в __init__ и
        сеттере. Гарантирует, что внутренний словарь содержит только
        нормализованные строки.

        Args:
            data (dict[str, str]): Словарь для нормализации.

        Returns:
            dict[str, str]: Новый словарь с нормализованными ключами и
                значениями.

        Raises:
            ValueError: Если входные данные не словарь или содержат
                нестроковые значения.
        """
        if not isinstance(data, dict):
            raise ValueError(
                f'Параметр words должен быть словарём, получено: {type(data).__name__}'
            )

        normalized: dict[str, str] = {}
        for key, value in data.items():
            # normalize_word выбросит ValueError, если ключ или значение не
            # строка.
            norm_key = self.normalize_word(key)
            norm_value = self.normalize_word(value)
            normalized[norm_key] = norm_value

        return normalized

    @property
    def words(self) -> dict[str, str]:
        """
        Возвращает копию словаря слов.

        Геттер возвращает копию, чтобы предотвратить модификацию
        внутреннего состояния объекта (_words) извне.

        Returns:
            dict[str, str]: Копия словаря пар слово-перевод.
        """
        # Создаем поверхностную копию. Так как значения - неизменяемые строки,
        # глубокое копирование не требуется, что улучшает производительность.
        return {**self._words}

    @words.setter
    def words(self, value: dict[str, str]) -> None:
        """
        Устанавливает новый словарь слов с валидацией и нормализацией.

        Сеттер использует _normalize_dict для обеспечения целостности данных.

        Args:
            value (dict[str, str]): Новый словарь пар слово-перевод.

        Raises:
            ValueError: Если переданные данные не проходят валидацию.
        """
        # Защита от изменения слов во время активной сессии.
        if self._session_active:
            raise ValueError('Нельзя менять слова во время активной тренировки.')

        # Делегируем валидацию и нормализацию защищённому методу
        self._words = self._normalize_dict(value)

    def start_zero_mistakes_training(self) -> TrainingSession:
        """
        Начинает тренировку до первой ошибки.

        Returns:
            TrainingSession: Объект сессии ZeroMistakesTraining.
        """
        if self._session_active:
            raise RuntimeError('Нельзя начать тренировку, если она уже начата.')
        self._session_active = True

        return ZeroMistakesTraining(self)

    def start_time_limited_training(
        self, time_limit: float = 60.0
    ) -> TimeLimitedTraining:
        """
        Начинает тренировку с ограничением по времени.

        Args:
            time_limit (float): Лимит времени в секундах. По умолчанию 60.0.

        Returns:
            TimeLimitedTraining: Объект сессии TimeLimitedTraining.
        """
        if self._session_active:
            raise RuntimeError('Нельзя начать тренировку, если она уже начата.')

        self._session_active = True

        return TimeLimitedTraining(self, time_limit)

    def end_session(self) -> None:
        """
        Завершает текущую тренировочную сессию.

        Сбрасывает флаг активности сессии.
        """
        if not self._session_active:
            raise RuntimeError('Нельзя завершить неактивную сессию.')

        # Сбрасываем состояние.
        self._session_active = False

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
            raise ValueError('Коллекция слов пуста. Добавьте слова.')

        return random.choice(list(self._words.keys()))

    def get_random_word_pair(self) -> tuple[str, str]:
        """
        Возвращает случайную пару (слово, перевод) для игрового режима.

        Returns:
            tuple[str, str]: Кортеж из слова и его перевода.

        Raises:
            ValueError: Если коллекция слов пуста.
        """
        if not self._words:
            raise ValueError('Коллекция слов пуста. Добавьте слова перед началом игры.')

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
                f'Параметр word должен быть строкой, получено: {type(word).__name__}'
            )

        if not isinstance(translation, str):
            raise ValueError(
                f'Параметр translation должен быть строкой, '
                f'получено: {type(translation).__name__}'
            )

        normalized_word = self.normalize_word(word)
        normalized_translation = self.normalize_word(translation)

        if normalized_word not in self._words:
            raise ValueError(f'Слово "{normalized_word}" отсутствует в коллекции.')

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
                f'Параметр word должен быть строкой, получено: {type(word).__name__}'
            )

        normalized_word = self.normalize_word(word)

        if normalized_word not in self._words:
            raise ValueError(f'Слово "{normalized_word}" отсутствует в коллекции.')

        return self._words[normalized_word]
