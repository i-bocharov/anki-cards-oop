import importlib
import tempfile
import os

from pathlib import Path

import pytest


@pytest.fixture()
def loader_cls():
    from anki import loader
    importlib.reload(loader)
    return loader.TextFileLoader


def test_TextFileLoader_class_has_no_class_attributes(loader_cls):
    """Атрибут file_path должен быть только у экземпляров"""
    assert not hasattr(loader_cls, "file_path"), (
        "Атрибут `file_path` должен определяться при инициализации экземпляра, а не на уровне класса"
    )


def test_TextFileLoader_accepts_only_keyword_arguments(loader_cls):
    """Параметр file_path должен быть только именованным"""
    with pytest.raises(TypeError):
        loader_cls("words.txt")  # Позиционный аргумент должен вызывать ошибку
        assert False, "Параметр `file_path` инициализатора должен быть только именованным"


def test_TextFileLoader_default_file_path(loader_cls):
    """По умолчанию должен использовать './words.txt'"""
    loader = loader_cls()

    assert loader.file_path == Path("./words.txt"), (
        "Атрибут `file_path` должен принимать значением по умолчанию \"./words.txt\""
    )
    assert isinstance(loader.file_path, Path), (
        "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
    )


def test_TextFileLoader_path_attributes_are_path_objects(loader_cls):
    """Атрибут file_path должен быть объектом Path"""
    loader1 = loader_cls()
    try:
        loader2 = loader_cls(file_path="custom.txt")
    except Exception:
        assert False, "Убедитесь, что класс `TextFileLoader` при инициализации принимает параметр `file_path`"

    assert isinstance(loader1.file_path, Path), (
        "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
    )
    assert isinstance(loader2.file_path, Path), (
        "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
    )


def test_TextFileLoader_accepts_string_path(loader_cls):
    """Должен принимать строковый путь и преобразовывать в Path"""
    try:
        loader = loader_cls(file_path="data/custom_words.txt")
    except Exception:
        assert False, "Убедитесь, что класс `TextFileLoader` при инициализации принимает параметр `file_path`"

    assert loader.file_path == Path("data/custom_words.txt"), (
        "Атрибут `file_path` должен инициализироваться переданным значением, преобразованным в объект класса `pathlib.Path`"
    )
    assert isinstance(loader.file_path, Path), (
        "Атрибут `file_path` должен инициализироваться переданным значением, преобразованным в объект класса `pathlib.Path`"
    )


def test_TextFileLoader_rejects_directory_path(loader_cls):
    """Должен отклонять пути к директориям как значение `file_path`"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(ValueError):
            loader_cls(file_path=temp_dir)
            assert False, "Атрибут `file_path` должен принимать значения, указывающие только на файл, не на директорию"


def test_TextFileLoader_accepts_nonexistent_file(loader_cls):
    """Должен принимать путь к несуществующему файлу (файл может быть создан позже)"""
    try:
        loader = loader_cls(file_path="nonexistent_file.txt")
    except Exception:
        assert False, "Атрибут `file_path` может принимать значения, указывающие на несуществующий файл"


