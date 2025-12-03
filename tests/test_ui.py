import importlib

import pytest

@pytest.fixture()
def ui_cls():
    from anki import ui
    importlib.reload(ui)
    return ui.TextUI



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

