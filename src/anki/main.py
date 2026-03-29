import argparse
import pathlib
from typing import Union

from anki.anki import Anki
from anki.loader import (
    BaseFileLoader,
    TextFileLoader,
    TSVFileLoader,
    JsonFileLoader,
    JsonNetworkLoader
)
from anki.ui import TextUI


def get_loader(source: str) -> Union[BaseFileLoader, JsonNetworkLoader]:
    """
    Выбирает реализацию загрузчика в зависимости от источника.

    Если source начинается с http/https, создаёт JsonNetworkLoader.
    Иначе выбирает загрузчик по расширению файла.

    Args:
        source (str): Путь к файлу или ссылка на сетевой ресурс.

    Returns:
        Union[BaseFileLoader, JsonNetworkLoader]: Экземпляр загрузчика.

    Raises:
        ValueError: Если источник не поддерживается.
    """

    # Сначала проверяем, является ли источник сетевой ссылкой.
    # Это должно идти ПЕРЕД проверкой расширения файла.
    if source.startswith('http://') or source.startswith('https://'):
        return JsonNetworkLoader(url=source)

    # Для локальных файлов выбираем по расширению.
    loaders = {
        '.txt': TextFileLoader,
        '.tsv': TSVFileLoader,
        '.json': JsonFileLoader
    }

    file_path = pathlib.Path(source)

    try:
        # suffix возвращает расширение файла
        loader = loaders[file_path.suffix]
        return loader(file_path=str(file_path))
    except KeyError:
        raise ValueError(f'Неизвестный тип источника слов: {source}')


def main():
    # Создали объект парсера аргументов командной строки.
    parser = argparse.ArgumentParser(prog='anki')

    # Добавили новый аргумент.
    parser.add_argument(
        '--source',
        default='./words.txt',
        help='Путь к файлу или ссылка на сетевой ресурс со словами',
        metavar='SOURCE_PATH',
    )

    # Распарсили аргументы командной строки.
    args = parser.parse_args()

    loader = get_loader(args.source)

    anki = Anki(words=loader.load_words())

    ui = TextUI(anki)
    ui.main_loop()

    loader.save_words(anki.get_words())


if __name__ == "__main__":
    main()
