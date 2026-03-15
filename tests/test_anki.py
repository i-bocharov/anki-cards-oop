import pytest
import importlib


@pytest.fixture()
def anki_cls():
    from anki import anki
    importlib.reload(anki)
    return anki.Anki


def test_Anki_class_has_no_class_attributes(anki_cls):
    """Атрибут words должен быть только у экземпляров"""
    assert not hasattr(anki_cls, "words"), (
        "Атрибут `words` должен определяться при инициализации экземпляра, а не на уровне класса"
    )


def test_Anki_accepts_only_keyword_arguments(anki_cls):
    """Параметр words должен быть только именованным"""
    with pytest.raises(TypeError):
        anki_cls({})  # Позиционный аргумент должен вызывать ошибку
        assert False, "Параметр `words` инициализатора должен быть только именованным"


def test_Anki_default_empty_dict(anki_cls):
    """По умолчанию words должен быть пустым словарём"""
    anki = anki_cls()
    assert anki.words == {}, (
        "При создании экземпляра класса без параметров, атрибут `words` должен инициализироваться пустым словарём"
    )
    assert isinstance(anki.words, dict)


def test_Anki_default_dict_is_not_shared(anki_cls):
    """Разные экземпляры должны иметь разные словари"""
    anki1 = anki_cls()
    anki2 = anki_cls()
    assert anki1.words is not anki2.words, (
        "Не используйте изменяемый объект как значение по умолчанию"
    )


def test_Anki_accepts_valid_dict(anki_cls):
    """Должен принимать словарь со строками"""
    valid_words = {"python": "питон", "hello": "привет"}
    anki = anki_cls(words=valid_words)
    assert anki.words == valid_words, (
        "При создании экземпляра класса с переданным словарём, атрибут `words` должен инициализироваться переданным словарём"
    )


def test_Anki_rejects_non_dict(anki_cls):
    """Должен отклонять не словари"""
    with pytest.raises(ValueError):
        anki_cls(words=[])
        assert False, "При создании экземпляра класса, параметр `words` должен принимать только словари."


def test_Anki_rejects_non_string_keys(anki_cls):
    """Должен отклонять не строковые ключи"""
    with pytest.raises(ValueError):
        anki_cls(words={1: "python"})
        assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все ключи - строки."


def test_Anki_rejects_non_string_values(anki_cls):
    """Должен отклнять не-строковые значения"""
    with pytest.raises(ValueError):
        anki_cls(words={"python": 1})
        assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все значения - строки."

def test_Anki_rejects_mixed_invalid_types(anki_cls):
    """Должен отклонять смешанные невалидные типы"""
    with pytest.raises(ValueError):
        anki_cls(words={1: 2, "valid": "invalid"})
        assert False, "При создании экземпляра класса, параметр `words` должен быть словарём, где все ключи и значения - строки."
