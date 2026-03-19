import pytest
import importlib.util

# Не то чтобы это тесты, которые действительно проверяют реализацию, но хотя бы попытку реализации
# проверят.


@pytest.mark.parametrize("module",
     [
        "anki.tests.test_anki",
        "anki.tests.test_loader",
        "anki.tests.test_integration",
    ]
)
def test_tests_file_exist(module):
    """Проверяет, что требуемые файлы были созданы"""
    spec = importlib.util.find_spec(module)
    assert spec is not None, f"Файл src/{module.replace('.', '/')}.py не найден"


@pytest.mark.parametrize("test_name", 
     [
        "test_anki_init_raises_ValueError_on_invalid_input",
        "test_anki_add_word_raises_ValueError_on_invalid_input"
     ]
 )
def test_test_anki_file_has_required_test_methods_defined(test_name):
    """Проверяет, что в файле test_anki.py были определены требуемые методы."""
    module = importlib.import_module("anki.tests.test_anki")

    assert hasattr(module, test_name), (
        f"В файле `test_anki.py` должен быть определён тест с именем {test_name}"
    )


def test_test_loader_file_has_required_test_methods_defined():
    """Проверяет, что в файле test_loader.py были определены требуемые методы."""
    test_name = "test_save_words_saves_words_as_comma_separated_values"
    module = importlib.import_module("anki.tests.test_loader")

    assert hasattr(module, test_name), (
        f"В файле `test_loader.py` должен быть определён тест с именем {test_name}"
    )


def test_test_integration_file_has_required_test_methods_defined():
    """Проверяет, что в файле test_integration.py были определены требуемые методы."""
    test_name = "test_integration"
    module = importlib.import_module("anki.tests.test_integration")

    assert hasattr(module, test_name), (
        f"В файле `test_integration.py` должен быть определён тест с именем {test_name}"
    )


