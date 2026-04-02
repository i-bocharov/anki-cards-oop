import argparse
from types import TracebackType
from typing import Literal

from anki.anki import Anki
from anki.loader import LoaderProtocol, loader_registry
from anki.ui import TextUI


class GameContext:
    """
    Контекстный менеджер для управления жизненным циклом игры.

    Гарантирует загрузку слов при входе в контекст и сохранение при выходе,
    даже если в теле контекста возникли ошибки.
    """

    def __init__(self, loader: LoaderProtocol, anki: Anki) -> None:
        """
        Инициализация контекстного менеджера.

        Args:
            loader (LoaderProtocol): Загрузчик слов.
            anki (Anki): Экземпляр игры Anki.
        """
        self.loader: LoaderProtocol = loader
        self.anki: Anki = anki

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
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """
        Сохраняет слова через загрузчик при выходе из контекста.

        Гарантирует сохранение даже при возникновении ошибок в теле контекста.
        Ошибки не подавляются и передаются дальше.

        Args:
            exc_type (type[BaseException] | None): Тип возникшего исключения.
            exc_val (BaseException | None): Значение исключения.
            exc_tb (TracebackType | None): Трассировка исключения.

        Returns:
            Literal[False]: Исключения не подавляются.
        """
        self.loader.save_words(self.anki.words)

        return False


def get_loader(source: str) -> LoaderProtocol:
    """
    Автоматически выбирает конкретную реализацию загрузчика,
    в зависимости от `source`.

    Args:
        source (str): Путь к файлу или ссылка на сетевой ресурс.

    Returns:
        LoaderProtocol: Экземпляр загрузчика.
    """
    loader_cls = loader_registry.get_loader(source)

    return loader_cls.from_source(source)


def main() -> None:
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


if __name__ == '__main__':
    main()
