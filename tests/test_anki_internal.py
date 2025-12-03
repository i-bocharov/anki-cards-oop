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


    def test_Anki_instanse_protected_atribute_words_exist(self, anki_instance):
        """Атрибут `_words` должен быть защищенным"""
        assert hasattr(anki_instance, "_words"), "Атрибут _words должен быть защищённым"
        assert not hasattr(anki_instance, "words")


    def test_Anki_class_has_no_class_attributes(self, anki_cls):
        """Атрибут `_words` должен быть только у экземпляров"""
        assert not hasattr(anki_cls, "_words"), (
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
        assert anki._words == {}, (
            "При создании экземпляра класса без параметров, атрибут `words` должен инициализироваться пустым словарём"
        )
        assert isinstance(anki._words, dict)


    def test_Anki_default_dict_is_not_shared(self, anki_cls):
        """Разные экземпляры должны иметь разные словари"""
        anki1 = anki_cls()
        anki2 = anki_cls()
        assert anki1._words is not anki2._words, (
            "Не используйте изменяемый объект как значение по умолчанию"
        )


    def test_Anki_accepts_valid_dict(self, anki_cls):
        """Должен принимать словарь со строками"""
        valid_words = {"python": "питон", "hello": "привет"}
        anki = anki_cls(words=valid_words)
        assert anki._words == valid_words, (
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
        assert anki._words == {"hello": "привет", "world": "мир"}, (
            "При инициализации класса `Anki` переданные в словаре `words` ключи и значения должны быть нормализованы."
        )

    def test_init_preserves_valid_words(self, anki_cls):
        """Корректные слова остаются без изменений"""
        words = {"hello": "привет", "world": "мир"}
        anki = anki_cls(words=words)
        assert anki._words == words, (
                "При передаче корректных значений в инит класса `Anki` не должно выполняться никаких преобразований."
        )


class TestAnkiAddWordMethod:
    """Коллекция тест-кейсов для тестирования метода `add_word()` класса `Anki`."""

    def test_add_word_normalizes_input(self, anki_instance):
        """Нормализация при добавлении"""
        anki_instance.add_word("  HELLO  ", " ПРИВЕТ ")
        assert anki_instance._words == {"hello": "привет"}, (
            "При добавлении слова методом `add_word` должна выполняться нормализация добавляемых слов и переводов"
        )

    def test_add_word_multiple_words(self, anki_instance):
        """Добавление нескольких слов"""
        anki_instance.add_word("HELLO", "ПРИВЕТ")
        anki_instance.add_word("WORLD", "МИР")
        assert anki_instance._words == {
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


class TestAnkiGetWordsMethod:
    """Коллекция тест-кейсов для тестирования метода `get_words()` класса `Anki`."""

    def test_get_word_method_exists(self, anki_instance):
        """У класса `Anki` должен быть метод `get_words()`"""

        assert hasattr(anki_instance, 'get_words'), (
            "У класса `Anki` должен быть определён метод `get_words()`."
        )
        assert callable(anki_instance.get_words), (
            "Атрибут `get_words` класса `Anki` должен быть методом."
        )

    def test_get_words_return_all_words(self, anki_cls):
        """Метод `get_words()` класса `Anki` должен возвращать все слова."""
        anki = anki_cls(words={"HELLO": "ПРИВЕТ"})
        assert anki.get_words() == {"hello": "привет"}, (
                "Метод `get_words()` должен возвращать все слова добавленные как при инициализации экземпляра, так и через метод `add_word()`"
        )
        anki.add_word("PyThOn", "Питон")

        assert anki.get_words() == {"hello": "привет", "python": "питон"}, (
                "Метод `get_words()` должен возвращать все слова добавленные как при инициализации экземпляра, так и через метод `add_word()`"
        )
        
    def test_get_words_return_a_copy_of_a_words_dict(self, anki_cls):
        """Метод `get_words()` класса `Anki` должен возвращать копию словаря `_words`"""
        anki = anki_cls(words={"HELLO": "ПРИВЕТ"})

        assert anki.get_words() is not anki._words


class TestAnkiClassDocstrings:

    def test_Anki_class_has_docstring(self, anki_cls):
        assert anki_cls.__doc__, (
            "Для класса `Anki` должен быть разработан докстринг"
        )

    def test_Anki_class_normalize_word_has_docstring(self, anki_cls):
        docstring = anki_cls.normalize_word.__doc__
        assert docstring, (
            "Для метода `normalize_word` класса `Anki` должен быть разработан докстринг"
        )
        assert "word" in docstring, (
            "В докстринге метода `normalize_word` должны быть описаны принимаемые параметры"
        )


    def test_Anki_class_add_word_has_docstring(self, anki_cls):
        docstring = anki_cls.add_word.__doc__
        assert docstring, (
            "Для метода `add_word` класса `Anki` должен быть разработан докстринг"
        )
        assert "word" in docstring, (
            "В докстринге метода `add_word` должен быть описаны параметр `word`"
        )
        assert "translation" in docstring, (
            "В докстринге метода `add_word` должен быть описаны параметр `translation`"
        )

    def test_Anki_class_get_words_has_docstring(self, anki_cls):
        assert anki_cls.get_words.__doc__, (
            "Для метода `get_words` класса `Anki` должен быть разработан докстринг"
        )


class TestAnkiMagicMethods:
    """Коллекция тест-кейсов для проверки переопределённых магических методов класса `Anki`"""

    def test_anki_has_custom_str_method(self, anki_cls):
        """Проверяет, что у класса Anki переопределён метод __str__"""
        assert "__str__" in anki_cls.__dict__, (
            "Класс Anki должен переопределять метод __str__"
        )

    def test_anki_has_custom_contains_method(self, anki_cls):
        """Проверяет, что у класса Anki переопределён метод __contains__"""
        assert '__contains__' in anki_cls.__dict__, (
            "Класс Anki должен переопределять метод __contains__"
        )

    def test_str_method_returns_custom_string(self, anki_instance):
        """Проверяет, что __str__ возвращает информативную строку"""
        result = str(anki_instance)

        assert not result.startswith("<anki.anki.Anki object at"), (
            "Метод __str__ должен возвращать кастомное представление"
        )

    def test_anki_custom_contains_method_uses_normalized_words(self, anki_cls):
        """
        Проверяет, что метод `__contains__` использует нормализованные слова
        для поиска наличия слов в словаре `_words`.
        """
        anki = anki_cls(words={"hello": "привет", "world": "мир"})

        assert "HELLO" in anki, (
            "Метод `__contains__` класса `Anki` должен быть регистронезависимым."
        )
        assert "hello" in anki, (
            "Метод `__contains__` вернул некорректные результаты для существующего слова"
        )
        assert "PYTHON" not in anki, (
            "Метод `__contains__` вернул некорректные результаты для несуществующего слова"
        )

    @pytest.mark.parametrize('invalid_input', [
        1,
        [],
        set()
    ])
    def test_anki_custom_contains_raises_ValueError_for_incorrect_input(self, invalid_input, anki_instance):
        """Проверят, что метод `__contains__` выбросит исключение `ValueError` в случае нестроковых входных данных"""
        with pytest.raises(ValueError):
            invalid_input in anki_instance
            assert False, (
                "Метод `__contains__` должен выбрасывать исключение `ValueError` для нестроковых данных."
            )





