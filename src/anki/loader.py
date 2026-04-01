from pathlib import Path
from typing import Protocol, Callable, TextIO, Self
import json
import requests


class LoaderProtocol(Protocol):
    """
    Протокол для загрузчиков.
    Гарантирует наличие методов load/save/from_source.
    """
    def load_words(self) -> dict[str, str]: ...
    def save_words(self, words: dict[str, str]) -> None: ...

    @classmethod
    def from_source(cls, source: str) -> Self: ...


class LoaderRegistry:
    """
    Реестр загрузчиков для динамической регистрации классов.
    """
    def __init__(self) -> None:
        self._registry: dict[
            type[LoaderProtocol],
            Callable[[str], bool]
        ] = {}

    def register(
        self,
        predicate: Callable[[str], bool],
    ) -> Callable[
        [type[LoaderProtocol]], type[LoaderProtocol]
    ]:
        """
        Регистрирует класс загрузчика с функцией-предикат.

        Args:
            predicate (Callable[[str], bool]): Функция, определяющая,
                подходит ли загрузчик для данного источника.

        Returns:
            Callable[[type[LoaderProtocol]], type[LoaderProtocol]]:
                Декоратор, который регистрирует класс и возвращает его.
        """
        def decorator(cls: type[LoaderProtocol]) -> type[LoaderProtocol]:
            self._registry[cls] = predicate
            return cls

        return decorator

    def get_loader(self, source: str) -> type[LoaderProtocol]:
        """
        Находит подходящий загрузчик для источника.

        Args:
            source (str): Путь или URL источника.

        Returns:
            type[LoaderProtocol]: Класс загрузчика.

        Raises:
            ValueError: Если подходящий загрузчик не найден.
        """
        for loader_cls, predicate in self._registry.items():
            if predicate(source):
                return loader_cls
        raise ValueError(f'Неизвестный источник: {source}')


loader_registry = LoaderRegistry()


class BaseFileLoader:
    """
    Базовый класс для загрузчиков файлов со словами.

    Реализует общую логику работы с файловой системой (открытие, закрытие,
    проверка путей), оставляя реализацию формата данных дочерним классам.
    """

    DEFAULT_FILE_PATH: str = './words.txt'

    def __init__(self, *, file_path: str | None = None) -> None:
        """
        Инициализация загрузчика.

        Args:
            file_path (str | None): Путь к файлу. Если не указан,
                используется DEFAULT_FILE_PATH.

        Raises:
            ValueError: Если путь указывает на директорию или находится
                вне безопасной зоны (Path Traversal).
        """
        if file_path is None:
            # Если путь не передали явно, используем значение
            # по умолчанию, определённое в теле класса.
            file_path = self.DEFAULT_FILE_PATH

        self._file_path: Path = Path(file_path)

        if self._file_path.exists() and self._file_path.is_dir():
            raise ValueError(
                f'Путь {file_path} является директорией, а должен быть файлом.'
            )

    def load_words(self) -> dict[str, str]:
        """
        Загружает слова из файла.

        Returns:
            dict[str, str]: Словарь пар слово-перевод. Пустой словарь,
                если файл не существует.
        """
        if not self._file_path.exists():
            return {}

        with self._file_path.open('r', encoding='utf-8') as f:
            return self._load_from_file(f)

    def save_words(self, words: dict[str, str]) -> None:
        """
        Сохраняет слова в файл.

        Args:
            words (dict[str, str]): Словарь с словами и переводами.

        Raises:
            ValueError: Если параметр words не является словарем или
                содержит нестроковые ключи/значения.
        """
        if not isinstance(words, dict):
            raise ValueError(
                'Значением параметра `words` должен быть словарь.'
            )

        # Валидация содержимого словаря
        for key, value in words.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(
                    'Ключи и значения словаря должны быть строками.'
                )

        with self._file_path.open('w', encoding='utf-8') as f:
            self._save_to_file(words, f)

    def _load_from_file(self, file_object: TextIO) -> dict[str, str]:
        """
        Реализует логику загрузки данных определённого формата из file_object.

        Метод должен быть переопределён в наследниках.

        Args:
            file_object (TextIO): FileLike объект,
                из которого идёт чтение данных.

        Returns:
            dict[str, str]: Словарь с загруженными словами.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError

    def _save_to_file(
            self, words: dict[str, str], file_object: TextIO
    ) -> None:
        """
        Реализует логику сохранения слов в определённом формате в файл.

        Метод должен быть переопределён в наследниках.

        Args:
            words (dict[str, str]): Словарь с словами и переводами.
            file_object (TextIO): FileLike объект,
                в который идёт запись данных.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError


@loader_registry.register(lambda s: s.endswith('.txt'))
class TextFileLoader(BaseFileLoader):
    """
    Загрузчик для текстовых файлов формата CSV (разделитель запятая).

    Формат записи: "слово,перевод"
    """

    DEFAULT_FILE_PATH: str = './words.txt'

    @classmethod
    def from_source(cls, source: str) -> Self:
        """
        Создаёт экземпляр загрузчика из источника.

        Args:
            source (str): Путь к файлу.

        Returns:
            Self: Экземпляр TextFileLoader.
        """
        return cls(file_path=source)

    def _load_from_file(self, file_object: TextIO) -> dict[str, str]:
        """
        Парсит строки файла в словарь (формат CSV).

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            dict[str, str]: Словарь пар слово-перевод.
        """
        words: dict[str, str] = {}
        for line in file_object:
            line_content = line.strip()
            if not line_content:
                continue

            # Безопасное разделение: только первое вхождение запятой.
            parts = line_content.split(',', 1)
            if len(parts) != 2:
                continue

            key, value = parts
            words[key.strip()] = value.strip()

        return words

    def _save_to_file(
            self, words: dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате CSV.

        Args:
            words (dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        for word, translation in words.items():
            # Санитизация данных: удаление переносов строк.
            clean_word = str(word).replace('\n', '').replace('\r', '')
            clean_translation = str(translation).replace('\n', '').replace(
                '\r', ''
            )
            file_object.write(f'{clean_word},{clean_translation}\n')


@loader_registry.register(lambda s: s.endswith('.tsv'))
class TSVFileLoader(BaseFileLoader):
    """
    Загрузчик для TSV файлов (разделитель табуляция).

    Формат записи: "слово\\tперевод"
    """

    DEFAULT_FILE_PATH: str = './words.tsv'

    @classmethod
    def from_source(cls, source: str) -> Self:
        return cls(file_path=source)

    def _load_from_file(self, file_object: TextIO) -> dict[str, str]:
        """
        Парсит строки TSV файла в словарь.

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            dict[str, str]: Словарь пар слово-перевод.
        """
        words: dict[str, str] = {}
        for line in file_object:
            line_content = line.strip()
            if not line_content:
                continue

            parts = line_content.split('\t', 1)
            if len(parts) != 2:
                continue

            key, value = parts
            words[key.strip()] = value.strip()

        return words

    def _save_to_file(
            self, words: dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате TSV.

        Args:
            words (dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        for word, translation in words.items():
            clean_word = str(word).replace('\n', '').replace('\r', '')
            clean_translation = str(translation).replace('\n', '').replace(
                '\r', ''
            )
            file_object.write(f'{clean_word}\t{clean_translation}\n')


@loader_registry.register(lambda s: s.endswith('.json'))
class JsonFileLoader(BaseFileLoader):
    """
    Загрузчик для файлов формата JSON.

    Формат записи: {"слово": "перевод", ...}
    """

    DEFAULT_FILE_PATH: str = './words.json'

    @classmethod
    def from_source(cls, source: str) -> Self:
        return cls(file_path=source)

    def _load_from_file(self, file_object: TextIO) -> dict[str, str]:
        """
        Загружает и парсит JSON данные из файла.

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            dict[str, str]: Словарь пар слово-перевод.
        """
        # Явная типизация и валидация.
        words: dict[str, str] = json.load(file_object)

        if not isinstance(words, dict):
            return {}

        for k, v in words.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError('Некорректные данные в файле JSON.')

        return words

    def _save_to_file(
            self, words: dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате JSON.

        Args:
            words (dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        json.dump(
            words,
            file_object,
            indent=2,
            ensure_ascii=False
        )


@loader_registry.register(lambda s: s.startswith(('http://', 'https://')))
class JsonNetworkLoader:
    """
    Загрузчик слов из сетевого источника по ссылке.

    Получает JSON данные по указанному URL и парсит их в словарь.
    Не наследуется от BaseFileLoader, так как работает с сетью, а не с файлами.
    """
    def __init__(self, url: str) -> None:
        """
        Инициализирует загрузчик с указанным URL.

        Args:
            url (str): Ссылка на источник данных в формате JSON.
        """
        if not url.startswith(('http://', 'https://')):
            raise ValueError('Небезопасный URL. Используйте http или https.')

        self.url: str = url

    @classmethod
    def from_source(cls, source: str) -> Self:
        """
        Создаёт экземпляр загрузчика из источника.

        Args:
            source (str): URL источника.

        Returns:
            Self: Экземпляр JsonNetworkLoader.
        """
        return cls(url=source)

    def load_words(self) -> dict[str, str]:
        """
        Загружает слова из сетевого источника по ссылке.

        Returns:
            dict[str, str]: Словарь пар слово-перевод.

        Raises:
            requests.RequestException: Если произошла ошибка при запросе.
            json.JSONDecodeError: Если ответ не валидный JSON.
        """
        response = requests.get(self.url)
        response.raise_for_status()

        # Явная типизация и валидация.
        words: dict[str, str] = response.json()

        for k, v in words.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError('Некорректные данные получены по сети.')

        return words

    def save_words(self, words: dict[str, str]) -> None:
        """
        Метод-заглушка для сохранения слов.

        Для сетевого загрузчика сохранение не реализовано.

        Args:
            words (dict[str, str]): Словарь с словами и переводами.
        """
        # Заглушка: сетевой загрузчик не поддерживает сохранение.
        pass
