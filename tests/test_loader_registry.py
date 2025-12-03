import importlib

import pytest

from anki.loader import TextFileLoader, TSVFileLoader, JsonFileLoader, JsonNetworkLoader, loader_registry


@pytest.fixture()
def registry_cls():
    from anki import loader
    importlib.reload(loader)
    return loader.LoaderRegistry


@pytest.fixture
def registry_instance(registry_cls):
    return registry_cls()


def test_loader_registry_class_exists():
    """Класс LoaderRegistry должен быть реализован в модуле loader.py"""
    from anki import loader

    assert hasattr(loader, "LoaderRegistry"), (
        "Убедитесь, что в модуле loader реализован класс `LoaderRegistry`"
    )


@pytest.mark.parametrize("method_name", ["register", "get_loader", "__init__"])
def test_loader_registry_has_expected_methods(registry_cls, method_name):
    """Класс `LoaderRegistry` должен реализовывать все необходимые методы."""
    assert hasattr(registry_cls, method_name), (
        "Убедитесь, что класс `LoaderRegistry` реализует все ожидаемые методы"
    )


def test_register_decorator_registers_object_in_registry(registry_instance):
    """Декоратор `register` должен регистрировать декорированные объекты в внутренний реестр."""

    def test_fn(source):
        return False

    @registry_instance.register(test_fn)
    class TestClass:
        ...

    assert registry_instance._registry[TestClass] == test_fn, (
        "Убедитесь, что декоратор `register` класса `LoaderRegistry` регистрирует стратегию и класс"
        " в реестре `_registry`"
    )


def test_get_loader_method_returns_object_from_registry(registry_instance):
    """
    Метод get_loader должен возвращать ранее зарегистрированные объекты при условии выполнения определённых
    в стратегии применимости загрузчика условий.
    """

    def test_fn(source):
        return True

    @registry_instance.register(test_fn)
    class TestClass:
        ...

    assert registry_instance.get_loader("identificator") == TestClass, (
        "Убедитесь, что метод `get_loader` возвращает декорированный ранее объект"
        " в случае если функция стратегия возвращает `True`."
    )


def test_get_loader_method_raises_ValueError_on_unknown_source(registry_instance):
    """Метод get_loader должен обрабывать неизвестные значения"""

    def test_fn(source):
        return False

    @registry_instance.register(test_fn)
    class TestClass:
        ...

    with pytest.raises(ValueError):
        registry_instance.get_loader("wrong")
        assert False, (
            "Убедитесь, что метод `get_loader` выбрасывает ошибку `ValueError`"
            "при получении неизвестного источника."
    )

@pytest.mark.parametrize("loader, source", [
    (TextFileLoader, "file.txt"),
    (TSVFileLoader, "words.tsv"),
    (JsonFileLoader, "webwords.json"),
    (JsonNetworkLoader, "http://localhost:8001/words"),
])
def test_users_registry_has_existing_loaders_registered(loader, source):
    try:
        assert loader_registry.get_loader(source) == loader
    except Exception as err:
        assert False, (
            f"Убедитесь что отметили класс загрузчика {loader.__name__} идентификатором {ident}"
        )
