import importlib

from unittest.mock import Mock, patch

import pytest


@pytest.fixture()
def ui_cls():
    from anki import ui
    importlib.reload(ui)
    return ui.TextUI


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


def test_TextUI_class_has_MENU_attribute(ui_cls):
    """В классе TextUI должен быть атрибут `MENU`."""
    assert hasattr(ui_cls, 'MENU'), (
        "В классе TextUI должен быть определён аттрибут класса `MENU`"
    )


def test_MENU_attribute_is_not_empty(ui_cls):
    """Атрибут `MENU` класса не должен быть пустым."""
    assert ui_cls.MENU != '', (
        "Атрибут `MENU` класса TextUI не должен быть пустым"
    )


def test_TextUI_class_has_STOP_WORD_attribute(ui_cls):
    """В классе TextUI должен быть атрибут `STOP_WORD`."""
    assert hasattr(ui_cls, 'STOP_WORD'), (
        "В классе TextUI должен быть определён аттрибут класса `STOP_WORD`"
    )


def test_STOP_WORD_attribute_is_not_empty(ui_cls):
    """Атрибут `STOP_WORD` класса не должен быть пустым."""
    assert ui_cls.STOP_WORD != '', (
        "Атрибут `STOP_WORD` класса TextUI не должен быть пустым"
    )

def test_TextUI_class_initialization_no_args(ui_cls):
    """При инициализации класса `TextUI` ожидается обязательный позиционный аргумент"""
    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        ui_cls()
        assert False, "Инициализатор класса `TextUI` должен принимать 1 обязательный позиционный аргумент - экземпляр класса `Anki`"


def test_TextUI_class_anki_instance_are_saved_in_anki_game_atribute(ui_cls, anki_instance):
    """При инициализации класса `TextUI` ожидается, что переданный экземпляр класса `Anki` будет сохранён в атрибут `_anki_game`"""
    assert not hasattr(ui_cls, "_anki_game"), (
        "Атрибут `_anki_game` должен быть объявлен при инициализации экземпляра класса"
    )

    ui = ui_cls(anki_instance)

    assert hasattr(ui, "_anki_game"), (
        "Переданный экземпляр класса `Anki` должен быть сохранён в атрибут `_anki_game`"
    )


@pytest.mark.parametrize("method_name", [
    "start_game",
    "add_words",
    "show_words",
    "main_loop"
])
def test_TextUI_class_has_main_loop_method(ui_cls, method_name):
    """В классе TextUI должны быть определёны требуемые методы"""

    assert hasattr(ui_cls, method_name), (
        f"В классе TextUI должен быть определён метод `{method_name}`"
    )


def test_TextUI_class_start_game_method(ui_cls, monkeypatch, capsys):
    """Проверяет метод `start_game` на предмет выполнения условий: вывод инфомрации о способе завершения, использование методов класса `Anki`"""
    anki_mock = Mock()
    anki_mock.get_random_word.return_value = "hello"

    ui = ui_cls(anki_mock)

    inputs = ["wrong"] * 3
    inputs.append(ui_cls.STOP_WORD)
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))

    try:
        ui.start_game()
    except StopIteration:
        assert False, (
            "Выполнение метода `start_game` должно прекращаться после ввода ключевого слова для выхода."
        )

    output = capsys.readouterr().out

    assert output, "Метод `start_game` должен выводить информацию для пользователя в стандартный поток вывода."

    assert ui_cls.STOP_WORD in output.splitlines()[0], (
        "Метод `start_game` должен выводить информацию о способе завершения игры сразу после начала своей работы в первой строке."
    )
    try:
        anki_mock.get_random_word.assert_called()
    except AssertionError:
        assert False, (
        "Метод `start_game` должен использовать методы экземпляра класса `Anki` для получения случайного слова"
    )
    

def test_TextUI_class_add_words_method(ui_cls, monkeypatch, capsys):
    """Проверяет метод `add_words` на предмет выполнения условий: вывод инфомрации о способе завершения, использование методов класса `Anki`"""
    anki_mock = Mock()

    ui = ui_cls(anki_mock)

    inputs = ["hello", "привет", "world", "мир", "   python   ", " питон", ui_cls.STOP_WORD] 
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.add_words()
    except StopIteration:
        assert False, (
            "Выполнение метода `add_words` должно прекращаться после ввода ключевого слова для выхода."
        )

    output = capsys.readouterr().out

    assert output, "Метод `add_words` должен выводить информацию для пользователя в стандартный поток вывода."
    assert ui_cls.STOP_WORD in output.splitlines()[0], (
        "Метод `add_words` должен выводить информацию о способе завершения игры сразу после начала своей работы в первой строке."
    )
    try:
        anki_mock.add_word.assert_called()
    except AssertionError:
        assert False, (
        "Метод `add_words` должен использовать методы экземпляра класса `Anki` для добавления слов"
    )


def test_TextUI_class_show_words_method(ui_cls, monkeypatch, capsys):
    """Проверяет метод `show_words` на предмент выполнения условий: вывода слов в формате "слово - перевод" и использование методов класса `Anki`"""
    anki_mock = Mock()
    anki_mock.get_words.return_value = {"hello": "привет", "world": "мир", "python": "питон"}

    ui = ui_cls(anki_mock)

    ui.show_words()

    output = capsys.readouterr().out

    assert output.splitlines() == ["hello - привет", "world - мир", "python - питон"], (
        "Метод `show_words` должен вывести информацию по словам в экземпляре класса `Anki`"
        " в стандартный поток вывода, в формате \"слово - перевод\""
    )

    try:
        anki_mock.get_words.assert_called()
    except AssertionError:
        assert False, (
        "Метод `show_words` должен использовать методы экземпляра класса `Anki` для получения слов"
    )


def test_TextUI_class_main_loop_method_shows_menu(ui_cls, anki_instance, monkeypatch, capsys):
    """Проверяет метод main_loop на предмет вывода меню"""
    ui = ui_cls(anki_instance)

    # меры предосторожности
    monkeypatch.setattr(ui, "start_game", Mock())
    monkeypatch.setattr(ui, "add_words", Mock())
    monkeypatch.setattr(ui, "show_words", Mock())

    inputs = ["5"]  # Выход
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.main_loop()
    except StopIteration:
        assert False, (
            "Выполнение метода `main_loop` должно прекращаться после ввода пункта меню для выхода."
        )
    output = capsys.readouterr().out
    assert ui_cls.MENU in output, "Меню пользовательского интерфейса должно выводиться при выполнении метода `main_loop`."


def test_TextUI_class_main_loop_method_handles_user_choices(ui_cls, anki_instance, monkeypatch, capsys):
    """Проверяет метод main_loop на предмет вывода меню"""
    ui = ui_cls(anki_instance)

    start_game_mock = Mock()
    add_words_mock = Mock()
    show_words_mock = Mock()

    monkeypatch.setattr(ui, "start_game", start_game_mock)
    monkeypatch.setattr(ui, "add_words", add_words_mock)
    monkeypatch.setattr(ui, "show_words", show_words_mock)

    # Старт игры, добавление слов, нереализованная фича, показ всех слов, выход
    inputs = ["1", "2", "3", "4", "5"]  
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.main_loop()
    except StopIteration:
        assert False, (
            "Выполнение метода `main_loop` должно прекращаться после ввода пункта меню для выхода."
        )
    output = capsys.readouterr().out
    assert "Данная функциональность ещё не реализована" in output, (
        "При выборе пункта меню \"Тренировка на время\" должна выводиться заглушка \"Данная функциональность ещё не реализована\"."
    )

    try:
        start_game_mock.assert_called_once()
    except AssertionError:
        assert False, (
            f"Во время проверки метода `main_loop`, количество вызовов метода `start_game`: {start_game_mock.call_count}, должно быть: 1."
        )

    try:
        add_words_mock.assert_called_once()
    except AssertionError:
        assert False, (
            f"Во время проверки метода `main_loop`, количество вызовов метода `add_words`: {add_words.call_count}, должно быть: 1."
        )

    try:
        show_words_mock.assert_called_once()
    except AssertionError:
        assert False, (
            f"Во время проверки метода `main_loop`, метод `show_words` был вызван {show_words_mock.call_count} раз, а должен был всего 1 раз."
        )

