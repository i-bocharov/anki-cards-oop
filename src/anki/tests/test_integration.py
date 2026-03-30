import os
import pathlib
import pytest
from anki.loader import TextFileLoader
from anki.anki import Anki


@pytest.fixture()
def tmp_integration_file():
    """
    Фикстура для интеграционных тестов.
    Создаёт чистый временный файл и удаляет его после теста.
    """
    path = pathlib.Path('./test_integration_words.txt')

    if path.exists():
        os.remove(path)
    yield str(path)
    if path.exists():
        os.remove(path)


def test_integration(tmp_integration_file):
    """
    Интеграционный тест взаимодействия TextFileLoader и Anki.
    Проверяет полный цикл.
    Загрузка -> работа с Anki -> сохранение -> верификация.
    """
    # Создаём TextFileLoader с временным файлом.
    loader = TextFileLoader(file_path=tmp_integration_file)

    # Загружаем слова методом load_words().
    loaded_words = loader.load_words()
    assert loaded_words == {}, 'Ожидался пустой словарь для нового файла'

    # Создаём Anki с загруженными словами.
    anki = Anki(words=loaded_words)

    # Проверяем, что свойство words возвращает правильные слова.
    assert anki.words == {}, (
        'Anki должен быть пустым после инициализации'
    )

    # Добавляем новое слово через add_word().
    anki.add_word('hello', 'привет')
    anki.add_word('world', 'мир')

    # Проверяем, что слова добавлены в память.
    words_in_memory = anki.words
    assert len(words_in_memory) == 2, 'В памяти должно быть 2 слова'
    assert words_in_memory['hello'] == 'привет'
    assert words_in_memory['world'] == 'мир'

    # Сохраняем слова через save_words().
    loader.save_words(words_in_memory)

    # Проверяем, что файл содержит все слова (исходные и новое).
    content = pathlib.Path(tmp_integration_file).read_text(encoding='utf-8')
    lines = content.strip().split('\n')

    assert len(lines) == 2, (
        f'Ожидалось 2 строки в файле, получено {len(lines)}'
    )

    assert 'hello,привет' in lines, 'Слово "hello" не найдено в файле'
    assert 'world,мир' in lines, 'Слово "world" не найдено в файле'

    loader2 = TextFileLoader(file_path=tmp_integration_file)
    reloaded_words = loader2.load_words()

    assert reloaded_words == words_in_memory, (
        'Перезагруженные слова должны совпадать с сохранёнными'
    )
