from typing import Dict, Optional


class Anki:
    def __init__(self, *, words: Optional[Dict[str, str]] = None):
        # Защита от изменяемого объекта по умолчанию
        if words is None:
            words = {}

        # Проверка типа контейнера
        if not isinstance(words, dict):
            raise ValueError(
                f'Параметр words должен быть словарём ,'
                f'получено: {type(words).__name__}'
            )

        # Валидация типов ключей и значений
        for key, value in words.items():
            if not isinstance(key, str):
                raise ValueError(
                    f'Ключ {key} должен быть строкой, '
                    f'получено: {type(key).__name__}'
                )
            if not isinstance(value, str):
                raise ValueError(
                    f'Значение для ключа {key} должно быть строкой, '
                    f'получено: {type(value).__name__}'
                )

        # Присваивание только после успешной валидации
        self.words = words
