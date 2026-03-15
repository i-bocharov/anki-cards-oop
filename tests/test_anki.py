import pytest
import importlib


@pytest.fixture()
def anki_cls():
    from anki import anki
    importlib.reload(anki)
    return anki.Anki


@pytest.fixture()
def anki_instance(anki_cls):
    return anki_cls()


class TestAnkiClassInitialization:
    """Коллекция тест-кейсов для проверки инициализатора класса Anki."""

    def test_Anki_class_has_no_class_attributes(self, anki_cls):
        """Атрибут words должен быть только у экземпляров"""
        assert not hasattr(anki_cls, "words"), (
            "Атрибут `words` должен определяться при инициализации экземпляра, а не на уровне класса"
        )


    def test_Anki_accepts_only_keyword_arguments(self, anki_cls):
        """Параметр words должен быть только именованным"""
        with pytest.raises(TypeError):
            anki_cls({})  # Позиционный аргумент должен вызывать ошибку
            assert False, "Параметр `words` инициализатора должен быть только именованным"


    def test_Anki_default_empty_dict(self, anki_cls):
        """По умолчанию words должен быть пустым словарём"""
        anki = anki_cls()
        assert anki.words == {}, (
            "При создании экземпляра класса без параметров, атрибут `words` должен инициализироваться пустым словарём"
        )
        assert isinstance(anki.words, dict)


    def test_Anki_default_dict_is_not_shared(self, anki_cls):
        """Разные экземпляры должны иметь разные словари"""
        anki1 = anki_cls()
        anki2 = anki_cls()
        assert anki1.words is not anki2.words, (
            "Не используйте изменяемый объект как значение по умолчанию"
        )


    def test_Anki_accepts_valid_dict(self, anki_cls):
        """Должен принимать словарь со строками"""
        valid_words = {"python": "питон", "hello": "привет"}
        anki = anki_cls(words=valid_words)
        assert anki.words == valid_words, (
            "При создании экземпляра класса с переданным словарём, атрибут `words` должен инициализироваться переданным словарём"
        )


    def test_Anki_rejects_non_dict(self, anki_cls):
        """Должен отклонять не словари"""
        with pytest.raises(ValueError):
            anki_cls(words=[])
            assert False, "При создании экземпляра класса, параметр `words` должен принимать только словари."


    def test_Anki_rejects_non_string_keys(self, anki_cls):
        """Должен отклонять не строковые ключи"""
        with pytest.raises(ValueError):
            anki_cls(words={1: "python"})
            assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все ключи - строки."


    def test_Anki_rejects_non_string_values(self, anki_cls):
        """Должен отклнять не-строковые значения"""
        with pytest.raises(ValueError):
            anki_cls(words={"python": 1})
            assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все значения - строки."

    def test_Anki_rejects_mixed_invalid_types(self, anki_cls):
        """Должен отклонять смешанные невалидные типы"""
        with pytest.raises(ValueError):
            anki_cls(words={1: 2, "valid": "invalid"})
            assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все ключи и значения - строки."

    def test_init_normalizes_words(self, anki_cls):
        """Нормализация слов при инициализации"""
        words = {"  HELLO  ": " ПРИВЕТ ", "WORLD": "  МИР  "}
        anki = anki_cls(words=words)
        assert anki.words == {"hello": "привет", "world": "мир"}, (
            "При инициализации класса `Anki` переданные в словаре `words` ключи и значения должны быть нормализованы."
        )

    def test_init_preserves_valid_words(self, anki_cls):
        """Корректные слова остаются без изменений"""
        words = {"hello": "привет", "world": "мир"}
        anki = anki_cls(words=words)
        assert anki.words == words, (
                "При передаче корректных значений в инит класса `Anki` не должно выполняться никаких преобразований."
        )


class TestAnkiAddWordMethod:
    """Коллекция тест-кейсов для тестирования метода `add_word()` класса `Anki`."""

    def test_add_word_normalizes_input(self, anki_instance):
        """Нормализация при добавлении"""
        anki_instance.add_word("  HELLO  ", " ПРИВЕТ ")
        assert anki_instance.words == {"hello": "привет"}, (
            "При добавлении слова методом `add_word` должна выполняться нормализация добавляемых слов и переводов"
        )

    def test_add_word_multiple_words(self, anki_instance):
        """Добавление нескольких слов"""
        anki_instance.add_word("HELLO", "ПРИВЕТ")
        anki_instance.add_word("WORLD", "МИР")
        assert anki_instance.words == {
            "hello": "привет",
            "world": "мир"
        }, (
            "При последовательном добавлении слов методом `add_word` должна выполняться нормализация добавляемых слов и переводов"
        )

    def test_add_word_validation(self, anki_instance):
        """Валидация параметров"""
        with pytest.raises(ValueError):
            anki_instance.add_word(123, "translation")
            assert False, "При передаче не строковых значений в метод `add_word` - метод должен выбрасывать исключение `ValueError`"

        with pytest.raises(ValueError):
            anki_instance.add_word("word", 456)
            assert False, "При передаче не строковых значений в метод `add_word` - метод должен выбрасывать исключение `ValueError`"


class TestAnkiNormalizeWordMethod:
    """Коллекция тест-кейсов для тестирования метода `normalize_word()` класса `Anki`."""

    def test_normalize_word_is_static_method(self, anki_cls):
        """Проверяем, что метод статический"""
        import types
        # Корректная ли это проверка? Или может просто вызывать и с класса, и с экземпляра?
        assert isinstance(anki_cls.normalize_word, types.FunctionType), (
            "Метод normalize_word должен быть статическим"
        )

    def test_normalize_word_removes_spaces(self, anki_cls):
        """Удаление пробельных символов"""
        assert anki_cls.normalize_word("  hello  ") == "hello", (
            "Метод `normalize_word` класса `Anki` должен удалять пробелы с обоих сторон переданного значения."
            )
        assert anki_cls.normalize_word("\tpython\n") == "python", (
            "Метод `normalize_word` класса `Anki` должен удалять любые пробельные символы с обоих сторон переданного значения."
        )

    def test_normalize_word_lowercase(self, anki_cls):
        """Приведение к нижнему регистру"""
        assert anki_cls.normalize_word("HeLLo") == "hello", (
            "Метод `normalize_word` класса `Anki` должен приводить слово к нижнему регистру."     
        )

    def test_normalize_word_combined(self, anki_cls):
        """Комбинированная нормализация"""
        assert anki_cls.normalize_word("  PyThOn  ") == "python", (
            "Метод `normalize_word` класса `Anki` должен приводить слово к нижнему регистру и"
            " удалять все пробельные символы с обоих сторон переданного значения"
            )

    def test_normalize_word_validation(self, anki_cls):
        """Валидация входных данных"""
        with pytest.raises(ValueError):
            anki_cls.normalize_word(123)
            assert False, (
                "Метод `normalize_word` должен выбрасывать исключение `ValueError` для нестроковых значений."
            )

        with pytest.raises(ValueError):
            anki_cls.normalize_word(None)
            assert False, (
                "Метод `normalize_word` должен выбрасывать исключение `ValueError` для нестроковых значений."
            )

