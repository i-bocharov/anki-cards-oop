import importlib

from unittest.mock import MagicMock

from anki.main import get_loader
from anki.loader import TextFileLoader, TSVFileLoader, JsonFileLoader, JsonNetworkLoader

import pytest


@pytest.fixture()
def game_context():
    from anki import main
    importlib.reload(main)
    try:
        game_context = main.GameContext
    except AttributeError:
        try:
            game_context = main.game_context
        except AttributeError:
            raise ValueError("Убедитесь что реализовали контекстный менеджер `GameContext` или `game_context`")

    return game_context


@pytest.mark.parametrize("source, loader_cls",
    [
        ("words.txt", TextFileLoader),   
        ("/tmp/words.txt", TextFileLoader),   
        ("words.tsv", TSVFileLoader),   
        ("words.json", JsonFileLoader),   
        ("http://example.com/words.txt", JsonNetworkLoader),   
        ("https://example.com/words.txt", JsonNetworkLoader),   
    ]
)
def test_get_loader_return_correct_loader(source, loader_cls):
    """
    Проверяет, что функция `get_loader` возвращает корректный загрузчик,
    в зависимости от того, какой параметр ей был передан.
    """
    assert isinstance(get_loader(source), loader_cls), (
        "Убедитесь, что `get_loader()` выбирает загрузчик в соответствии с описанной логикой"
    )


@pytest.mark.parametrize("source", ["db.sqlite3", "data"])
def test_get_loader_raises_ValueError_on_unkown_source(source):
    """Проверяет, что функция `get_loader()` выбрасывает исключения для неизвестных источников"""
    with pytest.raises(ValueError):
        get_loader(source)


def test_game_context_manager(game_context):
    """Проверяет корректность реализации контекстного менеджера для управления ходом игры."""
    # Здесь два разных словаря просто чтобы проверить, что методы действительно вызываются и
    # данные берутся из нужных мест.
    start_words = {"hello": "привет", "world": "мир"}
    end_words = {"python": "питон"}
    
    loader_mock = MagicMock()
    loader_mock.load_words.return_value = start_words

    anki_mock = MagicMock()

    try:
        with game_context(loader_mock, anki_mock):
            # Изменим слова, чтобы убедиться, что сохраняемые слова берутся из `words` класса `Anki`
            anki_mock.words = end_words
    except Exception as err:
        assert False, (
            f"Во время использования контекстного менеджера произошла ошибка {err}. Проверьте реализацию"
        )
    try:
        loader_mock.load_words.assert_called()
    except AssertionError:
        assert False, (
            f"Убедитесь что ваш контекстный менеджер использует метод `load_words` загрузчика для получения слов"
        )
    try:
        loader_mock.save_words.assert_called_with(end_words)
    except AssertionError:
        assert False, (
            f"Убедитесь, что ваш контекстный менеджер использует метод `save_words`"
            " для сохранения слов, полученных через геттер `words` класса `Anki"
        )

