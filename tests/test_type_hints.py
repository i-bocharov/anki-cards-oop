import os

import mypy.api
import pytest


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANKI_SRC = os.path.join(BASE_DIR, "..", "src", "anki")


@pytest.mark.parametrize("file_name", [
    "anki.py",
    "loader.py", 
    "main.py",
    "ui.py"
])
def test_mypy_reports_no_errors(file_name):
    """Проверка типизации проекта"""
    file_path = os.path.join(ANKI_SRC, file_name)

    result = mypy.api.run([
        "--check-untyped-defs",
		file_path
    ])

    stdout, stderr, exit_code = result

    if exit_code != 0:
        assert False, (
            f"Во время выполнения команды mypy --check-untyped-defs -m anki"
            f" возникли ошибки:{stdout}{stderr}"
        )
