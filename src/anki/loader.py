from pathlib import Path
from typing import Union, Dict


class TextFileLoader:
    """
    Утилита для безопасной работы с файлами словарей.
    Обеспечивает загрузку и сохранение пар «слово-перевод».
    Реализует защиту от уязвимостей пути.
    """
    def __init__(self, *, file_path: Union[str, Path] = './words.txt'):
        """
        Инициализирует загрузчик с валидацией пути к файлу.
        Проверяет тип данных и отсутствие обхода директорий.
        Гарантирует, что путь не ведет к папке.
        """
        # Валидация типа входных данных до конвертации.
        if not isinstance(file_path, (str, Path)):
            raise ValueError(
                f'Параметр file_path должен быть строкой или объектом Path, '
                f'получено: {type(file_path).__name__}'
            )

        path_obj = Path(file_path)

        # Защита от Path Traversal: явный запрет на использование '..'.
        if isinstance(file_path, str) and '..' in file_path:
            raise ValueError(
                'Путь не должен содержать "..". Обход директорий запрещен.'
            )

        # Проверка: путь не должен указывать на директорию.
        if path_obj.exists() and path_obj.is_dir():
            raise ValueError(
                f'Путь является директорией, а не файлом: {path_obj.resolve()}'
            )

        self._file_path = path_obj

    def load_words(self) -> Dict[str, str]:
        """
        Считывает пары слов из файла и возвращает словарь.
        Пропускает некорректные строки автоматически.
        Возвращает пустой словарь, если файл отсутствует.
        """
        if not self._file_path.exists():
            return {}

        words: Dict[str, str] = {}

        try:
            # Контекстный менеджер закроет файл и освободит ресурсы.
            with self._file_path.open('r', encoding='utf-8') as file:
                for line in file:
                    line_content = line.strip()

                    # Пропуск пустых строк.
                    if not line_content:
                        continue

                    # Строгая валидация: ровно одна запятая в строке.
                    if line_content.count(',') != 1:
                        continue

                    key, value = line_content.split(',', 1)
                    # Очистка от пробелов и сохранение пары.
                    words[key.strip()] = value.strip()

        except IOError:
            return {}

        return words

    def save_words(self, words: Dict[str, str]) -> None:
        """
        Перезаписывает файл данными из переданного словаря.
        Каждая пара записывается в отдельной строке.
        Формат записи: «слово,перевод».
        """
        # Валидация типа: метод принимает только словарь.
        if not isinstance(words, dict):
            raise ValueError(
                f'Параметр words должен быть словарём. '
                f'Получено: {type(words).__name__}'
            )

        try:
            # Контекстный менеджер закроет файл и освободит ресурсы.
            with self._file_path.open('w', encoding='utf-8') as file:
                for word, translation in words.items():
                    # Удаление переносов строк для сохранения формата.
                    clean_word = str(word).replace('\n', '').replace('\r', '')
                    clean_translation = str(translation).replace(
                        '\n', ''
                    ).replace('\r', '')

                    file.write(f'{clean_word},{clean_translation}\n')

                print(
                    f'Сохранено {len(words)} слов в файл {self._file_path}'
                )

        except IOError as e:
            raise RuntimeError(
                f'Не удалось записать в файл {self._file_path}: {e}'
            )
