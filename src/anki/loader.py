from pathlib import Path
from typing import Dict, Optional, TextIO
import json
import requests


class BaseFileLoader:
    """
    Базовый класс для загрузчиков файлов со словами.

    Реализует общую логику работы с файловой системой (открытие, закрытие,
    проверка путей), оставляя реализацию формата данных дочерним классам.
    """

    DEFAULT_FILE_PATH = './words.txt'

    def __init__(self, *, file_path: Optional[str] = None):
        """
        Инициализация загрузчика.

        Args:
            file_path (str, optional): Путь к файлу. Если не указан,
                используется DEFAULT_FILE_PATH.

        Raises:
            ValueError: Если путь указывает на директорию или находится
                вне безопасной зоны (Path Traversal).
        """
        if file_path is None:
            # Если путь не передали явно, используем значение
            # по умолчанию, определённое в теле класса.
            file_path = self.DEFAULT_FILE_PATH

        self._file_path = Path(file_path)

        if self._file_path.exists() and self._file_path.is_dir():
            raise ValueError(
                f'Путь {file_path} является директорией, а должен быть файлом.'
            )

    def load_words(self) -> Dict[str, str]:
        """
        Загружает слова из файла.

        Returns:
            Dict[str, str]: Словарь пар слово-перевод. Пустой словарь,
                если файл не существует.
        """
        if not self._file_path.exists():
            return {}

        with self._file_path.open('r', encoding='utf-8') as f:
            return self._load_from_file(f)

    def save_words(self, words: Dict[str, str]) -> None:
        """
        Сохраняет слова в файл.

        Args:
            words (Dict[str, str]): Словарь с словами и переводами.

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
            return self._save_to_file(words, f)

    def _load_from_file(self, file_object: TextIO) -> Dict[str, str]:
        """
        Реализует логику загрузки данных определённого формата из file_object.

        Метод должен быть переопределён в наследниках.

        Args:
            file_object (TextIO): FileLike объект,
                из которого идёт чтение данных.

        Returns:
            Dict[str, str]: Словарь с загруженными словами.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError

    def _save_to_file(
            self, words: Dict[str, str], file_object: TextIO
    ) -> None:
        """
        Реализует логику сохранения слов в определённом формате в файл.

        Метод должен быть переопределён в наследниках.

        Args:
            words (Dict[str, str]): Словарь с словами и переводами.
            file_object (TextIO): FileLike объект,
                в который идёт запись данных.

        Raises:
            NotImplementedError: Если метод не переопределён в наследнике.
        """
        raise NotImplementedError


class TextFileLoader(BaseFileLoader):
    """
    Загрузчик для текстовых файлов формата CSV (разделитель запятая).

    Формат записи: "слово,перевод"
    """

    DEFAULT_FILE_PATH = './words.txt'

    def _load_from_file(self, file_object: TextIO) -> Dict[str, str]:
        """
        Парсит строки файла в словарь (формат CSV).

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            Dict[str, str]: Словарь пар слово-перевод.
        """
        words: Dict[str, str] = {}
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
            self, words: Dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате CSV.

        Args:
            words (Dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        for word, translation in words.items():
            # Санитизация данных: удаление переносов строк.
            clean_word = str(word).replace('\n', '').replace('\r', '')
            clean_translation = str(translation).replace('\n', '').replace(
                '\r', ''
            )
            file_object.write(f'{clean_word},{clean_translation}\n')


class TSVFileLoader(BaseFileLoader):
    """
    Загрузчик для TSV файлов (разделитель табуляция).

    Формат записи: "слово\\tперевод"
    """

    DEFAULT_FILE_PATH = './words.tsv'

    def _load_from_file(self, file_object: TextIO) -> Dict[str, str]:
        """
        Парсит строки TSV файла в словарь.

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            Dict[str, str]: Словарь пар слово-перевод.
        """
        words: Dict[str, str] = {}
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
            self, words: Dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате TSV.

        Args:
            words (Dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        for word, translation in words.items():
            clean_word = str(word).replace('\n', '').replace('\r', '')
            clean_translation = str(translation).replace('\n', '').replace(
                '\r', ''
            )
            file_object.write(f'{clean_word}\t{clean_translation}\n')


class JsonFileLoader(BaseFileLoader):
    """
    Загрузчик для файлов формата JSON.

    Формат записи: {"слово": "перевод", ...}
    """

    DEFAULT_FILE_PATH = './words.json'

    def _load_from_file(self, file_object: TextIO) -> Dict[str, str]:
        """
        Загружает и парсит JSON данные из файла.

        Args:
            file_object (TextIO): Объект файла для чтения.

        Returns:
            Dict[str, str]: Словарь пар слово-перевод.
        """
        data = json.load(file_object)

        # Валидация: на всякий случай убеждаемся, что данные — это словарь.
        if not isinstance(data, dict):
            return {}

        return data

    def _save_to_file(
            self, words: Dict[str, str], file_object: TextIO
    ) -> None:
        """
        Записывает словарь в файл в формате JSON.

        Args:
            words (Dict[str, str]): Словарь для сохранения.
            file_object (TextIO): Объект файла для записи.
        """
        json.dump(
            words,
            file_object,
            indent=2,
            ensure_ascii=False
        )


class JsonNetworkLoader:
    """
    Загрузчик слов из сетевого источника по ссылке.

    Получает JSON данные по указанному URL и парсит их в словарь.
    Не наследуется от BaseFileLoader, так как работает с сетью, а не с файлами.
    """
    def __init__(self, url: str):
        """
        Инициализирует загрузчик с указанным URL.

        Args:
            url (str): Ссылка на источник данных в формате JSON.
        """
        self.url = url

    def load_words(self) -> Dict[str, str]:
        """
        Загружает слова из сетевого источника по ссылке.

        Returns:
            Dict[str, str]: Словарь пар слово-перевод.

        Raises:
            requests.RequestException: Если произошла ошибка при запросе.
            json.JSONDecodeError: Если ответ не валидный JSON.
        """
        response = requests.get(self.url)
        response.raise_for_status()
        return response.json()

    def save_words(self, words: Dict[str, str]) -> None:
        """
        Метод-заглушка для сохранения слов.

        Для сетевого загрузчика сохранение не реализовано.

        Args:
            words (Dict[str, str]): Словарь с словами и переводами.
        """
        # Заглушка: сетевой загрузчик не поддерживает сохранение.
        pass
