def test_project_is_installed_in_virtualenv():
    try:
        import anki
    except ModuleNotFoundError:
        assert False, "Убедитесь, что проект anki установлен в виртуальное окружение"


def test_anki_module_exists():
    try:
        import anki.anki
    except ModuleNotFoundError:
        assert False, "Убедитесь, что в проекте anki существует модуль `anki.py`"

def test_ui_module_exists():
    try:
        import anki.ui
    except ModuleNotFoundError:
        assert False, "Убедитесь, что в проекте anki существует модуль `ui.py`"

def test_loader_module_exists():
    try:
        import anki.loader
    except ModuleNotFoundError:
        assert False, "Убедитесь, что в проекте anki существует модуль `loader.py`"


def test_Anki_class_exists():
    import anki.anki
    try:
        anki.anki.Anki
    except AttributeError:
        assert False, "Убедитесь, что в модуле `anki.py` определена заготовка класса `Anki()`"


def test_TextUI_class_exists():
    import anki.ui
    try:
        anki.ui.TextUI
    except AttributeError:
        assert False, "Убедитесь, что в модуле `ui.py` определена заготовка класса `TextUI()`"

    

def test_TextFileLoader_class_exists():
    import anki.loader
    try:
        anki.loader.TextFileLoader
    except AttributeError:
        assert False, "Убедитесь, что в модуле `anki.py` определена заготовка класса `TextFileLoader()`"
