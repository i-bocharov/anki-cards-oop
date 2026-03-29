import argparse
import pathlib

from anki.anki import Anki
from anki.loader import (
    BaseFileLoader, TextFileLoader, TSVFileLoader, JsonFileLoader
)
from anki.ui import TextUI


def get_loader(source: str) -> BaseFileLoader:
    """
    Выбирает реализацию загрузчика в зависимости от расширения файла.

    Args:
        source (str): Путь к файлу для получения слов.

    Returns:
        BaseFileLoader: Экземпляр класса загрузчика соответствующего типа.

    Raises:
        ValueError: Если расширение файла не поддерживается.
    """

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
        '--source', default='./words.txt',
        help='Путь до источника со словами',
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
