from anki.main import get_loader
from anki.loader import TextFileLoader, TSVFileLoader, JsonFileLoader, JsonNetworkLoader

import pytest


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
