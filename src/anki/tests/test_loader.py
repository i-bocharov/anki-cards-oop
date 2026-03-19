import os
import pathlib

@pytest.fixture()
def tmp_file():
    # Создаём объект пути до файла.
    path = pathlib.Path("./test_words.txt")
    # Сохраняем слова в файл.
    path.write_text("hello,привет\n", encoding="utf-8")
    # Возвращаем путь до файла из фикстуры.
    yield str(path)

    # Удаляем созданный ранее файл.
    os.remove(path)
