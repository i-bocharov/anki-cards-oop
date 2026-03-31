import argparse
import pathlib
from typing import Union, Optional, Type

from anki.anki import Anki
from anki.loader import (
    BaseFileLoader,
    JsonNetworkLoader,
    loader_registry
)
from anki.ui import TextUI


class GameContext:
    """
    Контекстный менеджер для управления жизненным циклом игры.

    Гарантирует загрузку слов при входе в контекст и сохранение при выходе,
    даже если в теле контекста возникли ошибки.
    """
    def __init__(
            self,
            loader: Union[BaseFileLoader, JsonNetworkLoader],
            anki: Anki
    ):
        """
        Инициализация контекстного менеджера.

        Args:
            loader (Union[BaseFileLoader, JsonNetworkLoader]): Загрузчик слов.
            anki (Anki): Экземпляр игры Anki.
        """
        self.loader = loader
        self.anki = anki

    def __enter__(self) -> 'GameContext':
        """
        Загружает слова из источника и добавляет их в экземпляр Anki.

        Returns:
            GameContext: Сам экземпляр контекстного менеджера.
        """
        words = self.loader.load_words()
        self.anki.words = words
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[object]
    ) -> None:
        """
        Сохраняет слова через загрузчик при выходе из контекста.

        Гарантирует сохранение даже при возникновении ошибок в теле контекста.
        Ошибки не подавляются и передаются дальше.

        Args:
            exc_type (Optional[Type[BaseException]]): Тип возникшего исключения
                (если было).
            exc_val (Optional[BaseException]): Значение исключения (если было).
            exc_tb (Optional[object]): Трассировка исключения (если было).
        """
        self.loader.save_words(self.anki.words)
        # Возвращаем None (неявно), чтобы исключения не подавлялись.


def get_loader(source: str) -> Union[BaseFileLoader, JsonNetworkLoader]:
    """
    Автоматически выбирает конкретную реализацию загрузчика,
    в зависимости от `source`.

    Args:
        source (str): Путь к файлу или ссылка на сетевой ресурс.

    Returns:
        Union[BaseFileLoader, JsonNetworkLoader]: Экземпляр загрузчика.
    """
    if source.startswith('http'):
        identity = 'http'
        args = {'url': source}
    else:
        identity = pathlib.Path(source).suffix
        args = {'file_path': source}

    loader_cls = loader_registry.get_loader(identity)

    return loader_cls(**args)


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

    anki = Anki()

    with GameContext(loader, anki):
        ui = TextUI(anki)
        ui.main_loop()


if __name__ == "__main__":
    main()
