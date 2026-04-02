import os
import pathlib

import pytest

from anki.loader import TextFileLoader


@pytest.fixture()
def tmp_file():
    """
    Фикстура для тестов загрузки (с предзаполненным файлом).
    """
    # Создаём объект пути до файла.
    path = pathlib.Path('./test_words.txt')
    # Сохраняем слова в файл.
    path.write_text('hello,привет\n', encoding='utf-8')
    # Возвращаем путь до файла из фикстуры.
    yield str(path)

    # Удаляем созданный ранее файл.
    if path.exists():
        os.remove(path)


@pytest.fixture()
def tmp_save_file():
    """
    Фикстура для тестов.
    Возвращает путь к несуществующему файлу для чистой записи.
    """
    path = pathlib.Path('./test_words.txt')
    # Гарантируем что файл не существует перед тестом.
    if path.exists():
        os.remove(path)
    yield str(path)
    if path.exists():
        os.remove(path)


def test_save_words_saves_words_as_comma_separated_values(tmp_save_file):
    """
    Проверка, что слова сохраняются в файл в формате «слово,перевод».
    """
    # Подготавливаем данные и загрузчик.
    loader = TextFileLoader(file_path=tmp_save_file)
    test_words = {'hello': 'привет', 'world': 'мир', 'python': 'питон'}

    # Выполняем сохранение
    loader.save_words(test_words)

    # Проверяем результат
    assert pathlib.Path(tmp_save_file).exists(), 'Файл не был создан'

    content = pathlib.Path(tmp_save_file).read_text(encoding='utf-8')
    lines = content.strip().split('\n')

    # Проверка количества строк
    assert len(lines) == len(test_words), (
        f'Ожидалось {len(test_words)} строк, получено {len(lines)}'
    )

    # Проверка формата каждой строки (слово,перевод)
    for line in lines:
        # Формат: ровно одна запятая
        assert line.count(',') == 1, (
            f'Строка должна содержать ровно одну запятую: {line}'
        )

        word, translation = line.split(',', 1)

        # Проверка отсутствия лишних пробелов (данные очищены)
        assert word == word.strip(), 'В слове есть лишние пробелы'
        assert translation == translation.strip(), 'В переводе есть лишние пробелы'

        # Проверка отсутствия переносов строк внутри данных
        assert '\n' not in word and '\r' not in word, 'В слове есть переносы строк'
        assert '\n' not in translation and '\r' not in translation, (
            'В переводе есть переносы строк'
        )
