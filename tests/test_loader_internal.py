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


@pytest.fixture()
def empty_temp_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture()
def temp_file():
    """Создание временного файла для тестов"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("hello,привет\nworld,мир\npython,питон\n")
    yield f.name
    os.unlink(f.name)


@pytest.fixture()
def loader_with_empty_file(loader_cls, empty_temp_file):
    return loader_cls(file_path=empty_temp_file)


@pytest.fixture()
def loader_with_file(loader_cls, temp_file):
    return loader_cls(file_path=temp_file)


class TestTextFileLoaderClassInitialization:
    """Набор тест-кейсов для проверки инициализации класса `TextFileLoader`."""

    def test_TextFileLoader_class_has_protected_file_path_attribute(self, loader_with_file):
        assert not hasattr(loader_with_file, "file_path"), (
            "Атрибут `file_path` класса `TextFileLoader` должен быть защищённым"
        )
        assert hasattr(loader_with_file, "_file_path"), (
            "Для экземпляра класса `TextFileLoader` должен быть определён защищенный атрибут `_file_path`"
        )

    def test_TextFileLoader_class_has_no_class_attributes(self, loader_cls):
        """Атрибут file_path должен быть только у экземпляров"""
        assert not hasattr(loader_cls, "_file_path"), (
            "Атрибут `file_path` должен определяться при инициализации экземпляра, а не на уровне класса"
        )


    def test_TextFileLoader_accepts_only_keyword_arguments(self, loader_cls):
        """Параметр file_path должен быть только именованным"""
        with pytest.raises(TypeError):
            loader_cls("words.txt")  # Позиционный аргумент должен вызывать ошибку
            assert False, "Параметр `file_path` инициализатора должен быть только именованным"


    def test_TextFileLoader_default_file_path(self, loader_cls):
        """По умолчанию должен использовать './words.txt'"""
        loader = loader_cls()

        assert loader._file_path == Path("./words.txt"), (
            "Атрибут `file_path` должен принимать значением по умолчанию \"./words.txt\""
        )
        assert isinstance(loader._file_path, Path), (
            "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
        )


    def test_TextFileLoader_path_attributes_are_path_objects(self, loader_cls):
        """Атрибут file_path должен быть объектом Path"""
        loader1 = loader_cls()
        try:
            loader2 = loader_cls(file_path="custom.txt")
        except Exception:
            assert False, "Убедитесь, что класс `TextFileLoader` при инициализации принимает параметр `file_path`"

        assert isinstance(loader1._file_path, Path), (
            "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
        )
        assert isinstance(loader2._file_path, Path), (
            "Атрибут `file_path` должен инициализироваться объектом класса `pathlib.Path`"
        )


    def test_TextFileLoader_accepts_string_path(self, loader_cls):
        """Должен принимать строковый путь и преобразовывать в Path"""
        try:
            loader = loader_cls(file_path="data/custom_words.txt")
        except Exception:
            assert False, "Убедитесь, что класс `TextFileLoader` при инициализации принимает параметр `file_path`"

        assert loader._file_path == Path("data/custom_words.txt"), (
            "Атрибут `file_path` должен инициализироваться переданным значением, преобразованным в объект класса `pathlib.Path`"
        )
        assert isinstance(loader._file_path, Path), (
            "Атрибут `file_path` должен инициализироваться переданным значением, преобразованным в объект класса `pathlib.Path`"
        )


    def test_TextFileLoader_rejects_directory_path(self, loader_cls):
        """Должен отклонять пути к директориям как значение `file_path`"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError):
                loader_cls(file_path=temp_dir)
                assert False, "Атрибут `file_path` должен принимать значения, указывающие только на файл, не на директорию"


    def test_TextFileLoader_accepts_nonexistent_file(self, loader_cls):
        """Должен принимать путь к несуществующему файлу (файл может быть создан позже)"""
        try:
            loader = loader_cls(file_path="nonexistent_file.txt")
        except Exception:
            assert False, "Атрибут `file_path` может принимать значения, указывающие на несуществующий файл"


class TestTextFileLoaderClassLoadWordsMethod:
    """Набор тест-кейсов для тестирования метода `load_words()` класса `TextFileLoader`."""

    def test_load_words_returns_dict(self, loader_with_file):
        """Метод должен возвращать словарь"""
        words = loader_with_file.load_words()
        assert isinstance(words, dict), "Метод load_words должен возвращать словарь"

    def test_load_words_correct_parsing(self, loader_with_file):
        """Корректный парсинг содержимого файла"""
        words = loader_with_file.load_words()
        expected = {"hello": "привет", "world": "мир", "python": "питон"}
        assert words == expected

    def test_load_words_empty_file(self, loader_with_empty_file):
        words = loader_with_empty_file.load_words()
        assert words == {}, "При парсинге пустого файла метод `load_words()` должен возвращать пустой словарь."

    def test_load_words_nonexistent_file(self, loader_cls):
        """Обработка несуществующего файла"""
        loader = loader_cls(file_path="nonexistent_file.txt")
        words = loader.load_words()
        assert words == {}, "При парсинге несуществующего файла метод `load_words()` должен возвращать пустой словарь."


class TestTextFileLoaderClassSaveWordsMethod:

    def test_save_words_creates_file(self, loader_cls):
        """Если файла не существует, то при сохранении слов должен быть создан новый файл"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "words.txt"
            loader = loader_cls(file_path=str(file_path))

            words = {"test": "тест", "sample": "пример"}
            loader.save_words(words)

            assert file_path.exists(), (
                "Если файла не существует - должен быть создан новый файл"
            )

    def test_save_words_correct_content(self, loader_cls, temp_file):
        """Корректное содержимое сохранённого файла"""
        loader = loader_cls(file_path=temp_file)

        words = {"new": "новый", "data": "данные"}
        loader.save_words(words)

        with Path(temp_file).open('r') as f:
            content = f.read()

        expected_lines = {"new,новый\n", "data,данные\n"}
        actual_lines = set(content.splitlines(keepends=True))
        assert actual_lines == expected_lines, (
            "Содержимое файла после сохранения слов не соответствует ожидаемому"
        )

    def test_save_words_validation(self, loader_with_file):
        """Валидация входных данных"""
        with pytest.raises(ValueError):
            loader_with_file.save_words("not_a_dict")
            assert False, "Метод `save_words` должен выбрасывать ошибку, если в параметре `words` был передан не словарь"


class TestTextFileLoaderClassDocstrings:

    def test_TextFileLoader_class_has_docstring(self, loader_cls):
        assert loader_cls.__doc__, (
            "Для класса `TextFileLoader` должен быть разработан докстринг"
        )

    def test_TextFileLoader_class_load_words_has_docstring(self, loader_cls):
        docstring = loader_cls.load_words.__doc__
        assert docstring, (
            "Для метода `load_words` класса `TextFileLoader` должен быть разработан докстринг"
        )


    def test_TextFileLoader_class_save_words_has_docstring(self, loader_cls):
        docstring = loader_cls.save_words.__doc__
        assert docstring, (
            "Для метода `save_words` класса `TextFileLoader` должен быть разработан докстринг"
        )
        assert "words" in docstring, (
            "В докстринге метода `save_words` класса `TextFileLoader` должен быть описан параметр `words`"
        )

