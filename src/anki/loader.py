from pathlib import Path
from typing import Union


class TextFileLoader:
    def __init__(self, *, file_path: Union[str, Path] = './words.txt'):
        pass
        # Валидация типа входных данных до конвертации
        if not isinstance(file_path, (str, Path)):
            raise ValueError(
                f'Параметр file_path должен быть строкой или объектом Path, '
                f'получено: {type(file_path).__name__}'
            )

        # Преобразование в объект Path
        path_obj = Path(file_path)

        # Валидация: путь не должен быть директорией
        if path_obj.is_dir():
            raise ValueError(
                f'Путь является директорией, а не файлом: {path_obj.resolve()}'
            )

        # Сохранение в атрибут экземпляра
        self.file_path = path_obj
