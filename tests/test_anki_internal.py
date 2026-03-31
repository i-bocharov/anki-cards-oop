import pytest
import importlib
import unittest.mock
import traceback


@pytest.fixture()
def anki_cls():
    from anki import anki
    importlib.reload(anki)
    return anki.Anki


@pytest.fixture()
def anki_instance(anki_cls):
    return anki_cls()


@pytest.fixture()
def anki_with_words(anki_instance):
    anki_instance.add_word("hello", "привет")
    anki_instance.add_word("world", "мир")
    anki_instance.add_word("python", "питон")
    return anki_instance


class TestAnkiClassInitialization:
    """Коллекция тест-кейсов для проверки инициализатора класса Anki."""

    def test_Anki_instanse_protected_atribute_words_exist(self, anki_instance):
        """Атрибут `_words` должен быть защищенным"""
        assert hasattr(anki_instance, "_words"), "Атрибут _words должен быть защищённым"

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

    def test_init_uses_normalize_dict_method(self, anki_cls):
        """Инит класса должен использовать метод _normalize_dict"""
        with unittest.mock.patch.object(anki_cls, "_normalize_dict") as mock:
            words = {"hello": "привет", "world": "мир"}
            anki_cls(words=words)

        try:
            mock.assert_called_with(words)
        except AssertionError:
            assert False, (
                "Используйте метод `_normalize_dict` в ините класса для нормализации переданного словаря"
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

class TestAnkiWordsProperty:
    """Коллекция тест-кейсов для тестирования свойства `words` класса `Anki`."""

    def test_word_property_exists(self, anki_instance):
        """У класса `Anki` должено быть свойство `words`"""

        assert hasattr(anki_instance, 'words'), (
            "У класса `Anki` должно быть определно свойство `words`."
        )
        words_obj = getattr(type(anki_instance), "words", None)
        assert isinstance(words_obj, property), (
            "Атрибут `words` класса `Anki` должен быть свойством."
        )
        assert words_obj.fset is not None, (
            "Свойство `words` должно иметь сеттер"
        )

    def test_words_property_return_all_words(self, anki_cls):
        """Свойство `words` класса `Anki` должно возвращать все слова."""
        anki = anki_cls(words={"HELLO": "ПРИВЕТ"})
        assert anki.words == {"hello": "привет"}, (
                "Свойство `words` должно возвращать все слова добавленные как при инициализации экземпляра, так и через метод `add_word()`"
        )
        anki.add_word("PyThOn", "Питон")

        assert anki.words == {"hello": "привет", "python": "питон"}, (
                "Свойство `words` должно возвращать все слова добавленные как при инициализации экземпляра, так и через метод `add_word()`"
        )
        
    def test_words_property_return_a_copy_of_a_words_dict(self, anki_cls):
        """Свойство `words()` класса `Anki` должно возвращать копию словаря `_words`."""
        anki = anki_cls(words={"HELLO": "ПРИВЕТ"})

        assert anki.words is not anki._words


    def test_words_setter_replaces_words_dict(self, anki_instance):
        """Сеттер `words` должен полностью заменять словарь с словами."""
        old_words = anki_instance.words

        words = {"hello": "привет"}
        anki_instance.words = words

        assert anki_instance.words != old_words, (
            "Сеттер `words` должен полностью заменять словарь с словами в атрибуте `_words`."
        )
        assert anki_instance.words == words, (
            "Сеттер `words` должен полностью заменять словарь с словами в атрибуте `_words`."
        )

    def test_words_setter_calls_normalize_dict(self, anki_instance):
        """Сеттер свойства `words` должен использовать метод _normalize_dict."""
        with unittest.mock.patch.object(anki_instance, "_normalize_dict") as mock:
            words = {"hello": "привет", "world": "мир"}
            anki_instance.words = words

        try:
            mock.assert_called_with(words)
        except AssertionError:
            assert False, (
                "Используйте метод `_normalize_dict` в сеттере `words` для нормализации переданного словаря"
            )

    @pytest.mark.parametrize('invalid_input', [
        1,
        [],
        set(),
        "abc"
    ])
    def test_words_setter_raises_ValueError_on_invalid_input(self, anki_instance, invalid_input):
        """Через сеттер `words` можно установить только словари."""
        with pytest.raises(ValueError):
            anki_instance.words = invalid_input
            assert False, (
                    "Добавьте в сеттер `words` проверку, что переданное значения является словарем,"
                    " в противном случае - выбрасывайте ValueError."
            )


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

    def test_Anki_class_words_property_has_docstring(self, anki_cls):
        words_obj = getattr(anki_cls, "words", None)
        assert words_obj.__doc__, (
            "Для свойства `words` класса `Anki` должен быть разработан докстринг"
        )
        assert words_obj.fset.__doc__, (
            "Для сеттера свойства `words` класса `Anki` должен быть разработан докстринг"
        )

    def test_Anki_class_get_random_word_has_docstring(self, anki_cls):
        assert anki_cls.get_random_word.__doc__, (
            "Для метода `get_random_word` класса `Anki` должен быть разработан докстринг"
        )
        
    def test_Anki_class_check_translation_has_docstring(self, anki_cls):
        docstring = anki_cls.check_translation.__doc__
        assert docstring, (
            "Для метода `check_translation` класса `Anki` должен быть разработан докстринг"
        )
        assert "word" in docstring, (
            "В докстринге метода `check_translation` должен быть описаны параметр `word`"
        )
        assert "translation" in docstring, (
            "В докстринге метода `check_translation` должен быть описаны параметр `translation`"
        )

    def test_Anki_class_get_translation_has_docstring(self, anki_cls):
        docstring = anki_cls.get_translation.__doc__
        assert docstring, (
            "Для метода `get_translation` класса `Anki` должен быть разработан докстринг"
        )
        assert "word" in docstring, (
            "В докстринге метода `get_translation` должен быть описаны параметр `word`"
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

    def test_anki_has_iter_method(self, anki_with_words):
        """Проверяет что метод `__iter__()` был реализован"""

        try:
            iter(anki_with_words)
        except TypeError:
            assert False, "Убедитесь, что реализовали необходимые методы в классе `Anki`, чтобы сделать его итерируемым."

    def test_anki_has_len_method(self, anki_with_words):
        """Проверяет, что метод `__len__()` был реализован"""
        try:
            len(anki_with_words)
        except TypeError:
            assert False, "Убедитесь, что реализовали необходимые методы в классе `Anki`, чтобы определить количество слов через вызов `len()`"

    def test_anki_iter_method_returns_words_and_translations(self, anki_with_words):
        """Проверяет реализацию метода `__iter__()`"""
        words = {}
        for word, translation in anki_with_words:
            words[word] = translation

        assert words == anki_with_words.words, "Убедитесь, что при итерации по классу `Anki` возвращаются все слова."

    def test_anki_len_method_returns_correct_amount(self, anki_with_words):
        """Проверяет реализацию метода `__len__()`"""
        assert len(anki_with_words) == len(anki_with_words.words), (
            "Убедитесь, что вызов `len()` с экземпляром `Anki` возвращает правильное количество слов"
        )


class TestAnkiGetWordMethod:

    def test_get_random_word_raises_ValueError_if_no_words_exist(self, anki_instance):
        """Проверяет, что при отсутвии слов в игре, метод `get_random_word()` выбросит ошибку"""
        with pytest.raises(ValueError):
            anki_instance.get_random_word()
            assert False, (
                "Метод `get_random_word` должен выбрасывать исключение `ValueError` при отсутствии слов."
            )

    def test_get_random_word_returns_random_word(self, anki_with_words):
        """Проверяет, что метод `get_random_word()` выбирает случайное слово"""
        words = set()
        for _ in range(100):
            words.add(anki_with_words.get_random_word())

        assert len(words) > 1, (
            "Метод `get_word()` должен возвращать случайное слово из `_words`."
        )

        assert len(words & anki_with_words.words.keys()) == len(words), (
            "В итоговую выборку должны были попасть все слова из `_words`. Проверьте действительно ли слова возвращаются случайно а также"
            " используемый алгоритм случайного выбора."
        )


class TestAnkiCheckTranslationMethod:

    @pytest.mark.parametrize("word, translation",
        [
            ("HeLlo  ", "  Привет  "),
            ("\tWorld", "  Мир\t "),
            ("PYTHON", "питон"),
        ]
    )
    def test_check_translation_method_normalizes_input(self, anki_with_words, word, translation):
        """Проверяет, что метод `check_translation` использует нормализованное представление перевода и слова для проверки перевода"""
        assert anki_with_words.check_translation(word, translation) is True, (
            "Метод `check_translation` должен использовать номрализованное представление слова и перевода"
        )

    @pytest.mark.parametrize("word, translation",
        [
            ("Hello", "  Пока  "),
            ("\tWorld", "  Peace\t "),
            ("PYTHON", "анаконда"),
        ]
    )
    def test_check_translation_method_checks_correctness_of_a_translation(self, anki_with_words, word, translation):
        """Проверяет, что метод `check_translation` правильно определяет корректность перевода"""
        assert anki_with_words.check_translation(word, translation) is False, (
            "Метод `check_translation` должен правильно проверять корректность пользовательского перевода"
        )

    def test_check_translation_method_raises_for_unexistent_word(self, anki_instance):
        """Проверяет, что в случае отсутсвия слова, для которого запрошена проверка перевода, метод `check_translation` выбросит исключение"""
        with pytest.raises(ValueError):
            anki_instance.check_translation("abc", "abc")
            assert False, (
                "Метод `check_translation` должен выбрасывать исключение `ValueError` при отсутствии слова `word` в хранилище."
            )


class TestAnkiGetTranslationMethod:

    @pytest.mark.parametrize("word, translation",
        [
            ("HeLlo  ", "привет"),
            ("\tWorld", "мир"),
            ("PYTHON", "питон"),
        ]
    )
    def test_get_translation_method_returns_translation_for_normalized_input(self, anki_with_words, word, translation):
        """Проверяет, что метод `get_translation` использует нормализованное представление слова для поиска перевода"""
        assert anki_with_words.get_translation(word) == translation, (
            "Метод `get_translation` должен использовать нормализованное представление слова"
        )

    def test_get_translation_method_raises_for_unexistent_word(self, anki_instance):
        """Проверяет, что в случае отсутсвия слова, для которого запрошена проверка перевода, метод `check_translation` выбросит исключение"""
        with pytest.raises(ValueError):
            anki_instance.get_translation("abc")
            assert False, (
                "Метод `check_translation` должен выбрасывать исключение `ValueError` при отсутствии слова `word` в хранилище."
            )


class TestAnkiNormalizeDictMethod:

    def test_normalizes_dict(self, anki_instance):
        """Метод `_normalize_dict` должен выполнять нормализацию слов в словаре."""

        normalized_dict = anki_instance._normalize_dict(
            {
                "  HELLO  ": " ПРИВЕТ ",
                " PyThoN ": "питон\t",
            }
        )

        assert normalized_dict == {"hello": "привет", "python": "питон"}, (
            "Метод `_normalize_dict` должен выполнять нормализацию слов в переданном словаре"
            " и возвращать нормализованный словарь."
        )


class TestAnkiTrainingSession:

    @pytest.mark.parametrize('method', [
        "start_session",
        "end_session",
    ])
    def test_has_required_methods(self, anki_cls, method):
        assert hasattr(anki_cls, method), (
            f"Убедитесь что в классе `Anki` реализован метод {method}"
        )

    @pytest.mark.parametrize('attribute, default_value', [
        ("_session_active", False),
        ("_session_start_time", 0.0),
        ("_session_user_score", 0),
        ("last_session_stats", {"correct_answers": 0, "total_time": 0.0}),
    ])
    def test_has_required_attributes(self, anki_instance, attribute, default_value):
        assert hasattr(anki_instance, attribute), (
            f"Убедитесь что при создании объектов класса Anki инициализируется атрибут {attribute}"
            f"c значением {default_value}"
        )


    def test_check_translation_does_not_check_the_word_if_training_session_is_not_active(self, anki_with_words):
        """Проверка переданного слова (не его перевода), должна выполнять только если активна тренировка."""
        word = anki_with_words.get_random_word()

        try:
            anki_with_words.check_translation(word, "123abc")
        except ValueError:
            assert False, (
                "Убедитесь, что проверка переданного для угадывания слова методу `check_translation` работает"
                " только при активной тренировочной сессии"
            )

    def test_check_translation_method_works_in_active_training_session(self, anki_with_words):
        """
        При активной тренировке метод `check_translation` должен работать как ожидается:
            - Проверять корректность перевода
            - Увеличивать счётчик правильных ответов пользователя
        """
        words = anki_with_words.words
        
        anki_with_words.start_session() 
        try:
            for _ in range(3):
                word = anki_with_words.get_random_word()
                translation = words[word]
                anki_with_words.check_translation(word, translation)
        except Exception as err:
            assert False, (
                f"Во время нормального алгоритма работы с тренировочной сессией возникла ошибка: {err}."
            )
        anki_with_words.end_session()

        # 3 потому что по циклу 3 раза правильно угадываем перевод.
        assert anki_with_words.last_session_stats["correct_answers"] == 3, (
                "Убедитесь, что подсчёт результатов ведётся корректно",
                f"Ожидалось: 3 правильных ответа, получено: {anki_with_words.last_session_stats['correct_answers']}"
        )

    def test_attempt_to_translate_incorrect_word_result_in_ValuError(self, anki_instance):
        """
        При активной тренировке метод `check_translation` должен проверять,
        что переданный `word` является именно тем словом, которое было выдано
        для перевода.
        """

        anki_instance.add_word("python", "питон")

        anki_instance.start_session() 
        anki_instance.get_random_word()
        
        with pytest.raises(ValueError):
            anki_instance.check_translation("hello", "привет")
            assert False, (
                "Проверьте вашу реализацию защиты от накрутки через перевод случайных слов, вместо выданного ранее"
            )

    def test_attempt_to_translate_word_without_getting_the_word_result_in_ValueError(self, anki_instance):
        """
        При активной тренировке метод `check_translation` дожен проверять перевод только в том случае,
        если было получено новое слово.
        """

        anki_instance.add_word("python", "питон")

        anki_instance.start_session() 
        anki_instance.get_random_word()
        anki_instance.check_translation("python", "питон")

        with pytest.raises(ValueError):
            anki_instance.check_translation("python", "питон")
            assert False, (
                "Проверьте вашу реализацию защиты от накрутки: сейчас можно проверить перевод слова повторно"
                " без вызова метода `get_random_word()"
            )

    def test_cannot_change_whole_dict_of_words_if_training_is_active(self, anki_with_words):
        """При активной тренировке нельзя изменять словарь `words`"""

        anki_with_words.start_session()

        with pytest.raises(ValueError):
            anki_with_words.words = {"hello": "world"}
            assert False, (
                "При активной тренировке нужно запрещать изменять слова через сеттер свойства `words`"
            )

        anki_with_words.end_session()

        try:
            anki_with_words.words = {"hello": "world"}
        except ValueError:
            assert False, (
                "После завершения тренировки - нужно разрешать изменять слова через сеттер свойства `words`"
            )

    def test_start_and_end_session_methods_manage_session_state(self, anki_with_words):
        """
        Метод `start_session` должен начинать новую тренировку.
        Метод `end_session` должен завершать текущую активную сессию тренировки.
        """

        assert anki_with_words._session_active is False, (
            "Убедитесь что значение атрибута `_session_active` по-умолчанию выставлено в False."
        )

        anki_with_words.start_session()
        assert anki_with_words._session_active, (
            "Метод `start_session()` должен начинать тренировку, выставляя атрибут `_session_active` в `True`"
        )
        assert anki_with_words._session_start_time > 0, (
            "Метод `start_session()` должен сохранять время начала тренировки в атрибут `_session_start_time`"
        )

        anki_with_words.end_session()
        assert anki_with_words._session_active is False, (
            "Метод `end_session()` должен завершать тренировку, выставляя атрибут `_session_active` в `False`"
        )
        assert anki_with_words._session_start_time == 0, (
            "Метод `end_session()` должен сбрасывать время начала тренировки в значение `0.0`"
        )

        assert anki_with_words.last_session_stats["total_time"] > 0, (
            "Метод `end_session()` должен сохранять статистику текущей игровой сессии"
        )

    def start_session_method_raises_ValueError_if_session_is_already_active(self, anki_with_words):
        """Если уже активна тренировочная сессия - метод `start_sesion` должен выбрасывать ошибку RuntimeError."""

        anki_with_words.start_session()

        with pytest.raises(RuntimeError):
            anki_with_words.start_session()
            assert False, (
                "В случае активной тренировки, повторный вызов метода `start_session()` должен"
                " результировать в ошибке RuntimeError"
            )

    def end_session_method_raises_ValueError_if_session_is_not_active(self, anki_with_words):
        """Метод `end_session` должен выбрасывать ошибку RuntimeError если тренировочная сессия не активна."""

        with pytest.raises(RuntimeError):
            anki_with_words.end_session()
            assert False, (
                "В случае отсутствия активной тренировки, вызов метода `end_session()` должен"
                " результировать в ошибке RuntimeError"
            )
