import importlib

from unittest.mock import Mock, MagicMock, patch

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


@pytest.fixture()
def exit_choice_finder():
    def _exit_choice_finder(ui):
        commands = ui.get_available_commands()
        for idx, (func, desc) in enumerate(commands, 1):
            if func == ui.stop:
                return str(idx)
        raise ValueError("Нет способа остановить игру")
    return _exit_choice_finder


def test_TextUI_class_does_not_have_MENU_attribute(ui_cls):
    """В классе TextUI НЕ должено быть атрибут `MENU` - теперь он генерируется динамически."""
    assert hasattr(ui_cls, 'MENU') is False, (
        "В классе TextUI не должено быть определёно аттрибута класса `MENU` - меню формируется динамически."
    )


def test_TextUI_class_has_stop_method(ui_cls):
    """В классе TextUI должен быть метод `stop` для остановки главного цикла."""
    assert hasattr(ui_cls, 'stop'), (
        "В классе TextUI должен быть определён метод `stop` для остановки главного цикла."
    )


def test_TextUI_toggles_is_running_flag(ui_cls, anki_instance):
    """Метод `stop` должен выставлять значение флага `is_running` в False"""
    ui = ui_cls(anki_instance)
    ui._is_running = True

    ui.stop()

    assert ui._is_running is False, (
        "Метод `stop` должен выставлять значение флага `is_running` в False"
    )

def test_commands_definition_attribute_is_defined_at_initialization(ui_cls, anki_instance):
    """Атрибут `_command_definition` класса не должен быть пустым."""
    ui = ui_cls(anki_instance)
    assert hasattr(ui, "_command_definition"), (
        "Убедитесь, что при создании экземпляра класса TextUI инициализируется защищённый атрибут `_command_definition`"
    )
    for func, desc, predicate in ui._command_definition:
        assert callable(func), (
            "Убедитесь, что первым элементом в кортеже команд из `_command_definition` используется функция"
        )
        assert isinstance(desc, str), (
            "Убедитесь, что вторым элементом в кортеже команд из `_command_definition` используется строка"
        )
        assert callable(predicate), (
            "Убедитесь, что третьим элементом в кортеже команд из `_command_definition` используется функция"
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


def test_TextUI_class_show_words_method(ui_cls, anki_cls, monkeypatch, capsys):
    """Проверяет метод `show_words` на предмент выполнения условий: вывода слов в формате "слово - перевод" и использование методов класса `Anki`"""
    anki_mock = MagicMock()
    words = {"hello": "привет", "world": "мир", "python": "питон"}
    anki_mock.__iter__.return_value = iter(words.items())
    anki_mock.__len__.return_value = len(words)

    ui = ui_cls(anki_mock)

    ui.show_words()

    output = capsys.readouterr().out.splitlines()
    
    try:
        first_line = output.pop(0)
    except IndexError:
        assert False, "Метод `show_words` должен вывести информацию по словам в экземпляре класса `Anki`"

    assert str(len(words)) in first_line, "Метод `show_words` должен вывести информацию о количестве слов в первой строчке."

    try:
        anki_mock.get_words.assert_not_called()
    except AssertionError:
        assert False, (
            "Метод `show_words`не должен использовать метод `get_words()` экземпляра класса `Anki` для получения слов"
    )

    assert output == ["hello - привет", "world - мир", "python - питон"], (
        "Метод `show_words` должен вывести информацию по словам в экземпляре класса `Anki`"
        " в стандартный поток вывода, в формате \"слово - перевод\""
    )

    try:
        anki_mock.__iter__.assert_called()
    except AssertionError:
        assert False, (
            "Метод `show_words` должен использовать цикл `for` для получения всех слов и переводов в классе `Anki`"
    )

    try:
        anki_mock.__len__.assert_called()
    except AssertionError:
        assert False, (
            "Метод `show_words` должен использовать стандартную функцию `len()` для получения количества слов в `Anki`"
    )

def test_TextUI_class_train_until_mistake_method(ui_cls, anki_cls, monkeypatch, capsys):
    """
    Проверяет работоспособность метода `train_until_mistake`. По сути только использование нужных методов
    и выход из тренировки при некорректном переводе.
    """
    check_results = iter([True, True, False])

    anki_mock = Mock()
    anki_mock.get_random_word.return_value = "hello"
    anki_mock.check_translation.side_effect = [True, True, False]
    anki_mock.last_session_stats = {"correct_answers": 100500, "total_time": 999.99}

    ui = ui_cls(anki_mock)

    inputs = ["translation"] * 3
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))

    try:
        ui.train_until_mistake()
    except StopIteration:
        assert False, (
            "Выполнение метода `train_until_mistake` должно прекращаться после ввода некорректного перевода."
        )

    output = capsys.readouterr().out

    assert output, "Метод `train_until_mistake` должен выводить информацию для пользователя в стандартный поток вывода."
    assert "100500" in output, (
        "Метод `train_until_mistake` должен выводить информацию о количестве успешных ответов."
    )
    assert "999.99" in output, (
        "Метод `train_until_mistake` должен выводить информацию о времени игры."
    )

    try:
        anki_mock.start_session.assert_called()
    except AssertionError:
        assert False, (
        "Метод `start_session` должен использовать методы экземпляра класса `Anki` для начала тренировки"
    )

def test_TextUI_class_main_loop_method_shows_menu(ui_cls, anki_with_words, exit_choice_finder, monkeypatch, capsys):
    """Проверяет метод main_loop на предмет вывода меню"""
    # меры предосторожности
    monkeypatch.setattr(ui_cls, "start_game", Mock())
    monkeypatch.setattr(ui_cls, "add_words", Mock())
    monkeypatch.setattr(ui_cls, "show_words", Mock())

    ui = ui_cls(anki_with_words)

    inputs = [exit_choice_finder(ui)]  # Выход
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.main_loop()
    except StopIteration:
        assert False, (
            "Выполнение метода `main_loop` должно прекращаться после ввода пункта меню для выхода."
        )
    output = capsys.readouterr().out
    
    for (func, desc) in ui.get_available_commands():
        assert desc in output, (
            "Пункт меню {desc} пользовательского интерфейса должен выводиться при выполнении метода `main_loop`."
        )


def test_TextUI_class_main_loop_method_handles_user_choices(ui_cls, anki_with_words, exit_choice_finder, monkeypatch, capsys):
    """Проверяет метод main_loop на предмет вывода меню"""
    start_game_mock = Mock()
    add_words_mock = Mock()
    show_words_mock = Mock()
    train_until_mistake_mock = Mock()
    find_translation_mock = Mock()

    monkeypatch.setattr(ui_cls, "start_game", start_game_mock)
    monkeypatch.setattr(ui_cls, "add_words", add_words_mock)
    monkeypatch.setattr(ui_cls, "show_words", show_words_mock)
    monkeypatch.setattr(ui_cls, "train_until_mistake", train_until_mistake_mock)
    monkeypatch.setattr(ui_cls, "find_translation", find_translation_mock)

    ui = ui_cls(anki_with_words)

    # Старт игры, добавление слов, тренировка, поиск перевода, показ всех слов, выход
    inputs = ["1", "2", "3", "4", "5", exit_choice_finder(ui)]  
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.main_loop()
    except StopIteration:
        assert False, (
            "Выполнение метода `main_loop` должно прекращаться после ввода пункта меню для выхода."
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

    try:
        train_until_mistake_mock.assert_called_once()
    except AssertionError:
        assert False, (
            f"Во время проверки метода `main_loop`, метод `train_until_mistake` был вызван {train_until_mistake_mock.call_count} раз, а должен был всего 1 раз."
        )

    try:
        find_translation_mock.assert_called_once()
    except AssertionError:
        assert False, (
            f"Во время проверки метода `main_loop`, метод `find_translation` был вызван {find_translation.call_count} раз, а должен был всего 1 раз."
        )


def test_TextUI_class_find_translation_method_known_word(ui_cls, anki_instance, monkeypatch, capsys):
    """Проверяет работу метода `find_translation` - должен возвращать перевод для существующего слова"""
    anki_instance.add_word("python", "питон")

    ui = ui_cls(anki_instance)

    inputs = ["python"] 
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.find_translation()
    except StopIteration:
        assert False, (
            "Выполнение метода `find_translation` должно прекращаться после вывода информации"
            " о переводе или его отсутсвии."
        )

    output = capsys.readouterr().out

    assert output, "Метод `find_translation` должен выводить информацию для пользователя в стандартный поток вывода."
    assert "питон" in output, (
        "Метод `find_translation` должен вывести перевод для существующего слова"
    )


def test_TextUI_class_find_translation_method_unknown_word(ui_cls, anki_instance, monkeypatch, capsys):
    """Проверяет работу метода `find_translation` - не должен возвращать переводы в случае несуществсующего слова"""
    anki_instance.add_word("hello", "привет")

    ui = ui_cls(anki_instance)

    inputs = ["python"] 
    inputs = iter(inputs)

    monkeypatch.setattr('builtins.input', lambda x=None: next(inputs))
    
    try:
        ui.find_translation()
    except StopIteration:
        assert False, (
            "Выполнение метода `find_translation` должно прекращаться после вывода информации"
            " о переводе или его отсутсвии."
        )

    output = capsys.readouterr().out

    assert output, "Метод `find_translation` должен выводить информацию для пользователя в стандартный поток вывода."
    assert "привет" not in output, (
        "Метод `find_translation` не должен выводить перевод для несуществующего слова"
    )
