from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from anki.anki import Anki


class TextUI:
    """
    Класс для взаимодействия с пользователем и отрисовки текстового интерфейса.

    Использует экземпляр класса Anki для игровой логики и управления словами.
    Реализует меню, игровой режим и управление коллекцией слов.
    """

    # Константа для завершения игры.
    STOP_WORD: str = 'СТОП'

    def __init__(self, anki_game: 'Anki') -> None:
        """
        Инициализирует интерфейс с экземпляром игры Anki.

        Args:
            anki_game ('Anki'): Экземпляр класса Anki для игровой логики.
        """
        # Сохраняем ссылку на экземпляр Anki для использования в методах.
        self._anki_game: 'Anki' = anki_game
        self._is_running: bool = False

        # (Функция-обработчик, описание, условие_видимости)
        self._command_definition: list[
            tuple[Callable[..., None], str, Callable[..., bool]]
        ] = [
            (self.start_game, 'Начать игру', lambda: len(self._anki_game) > 0),
            (self.add_words, 'Добавить слова', lambda: True),
            (self.train_until_mistake, 'Тренировка до первой ошибки',
             lambda: len(self._anki_game) > 0),
            (self.show_words, 'Показать все слова',
             lambda: len(self._anki_game) > 0),
            (self.find_translation, 'Найти перевод',
             lambda: len(self._anki_game) > 0),
            (self.stop, 'Выход', lambda: True),
        ]

    def stop(self) -> None:
        """
        Останавливает главный цикл приложения.

        Устанавливает флаг _is_running в False, что приводит к завершению
        цикла main_loop().
        """
        self._is_running = False

    def start_game(self) -> None:
        """
        Запускает игровой режим для перевода слов.

        Пользователь вводит переводы случайных слов.
        Игра завершается при вводе STOP_WORD.
        """
        # Проверяем наличие слов перед началом игры.
        try:
            # Пытаемся получить случайное слово для проверки.
            self._anki_game.get_random_word()
        except ValueError:
            print('Слов для игры нет. Добавьте слова через меню.')
            return

        # Сообщаем пользователю о способе завершения.
        print(f'Чтобы закончить, введите слово "{self.STOP_WORD}"')

        while True:
            try:
                # Получаем случайную пару (слово, перевод) из Anki.
                word = self._anki_game.get_random_word()

                # Выводим слово для перевода.
                print(f'\nВаше слово для перевода: {word}')

                # Получаем ответ пользователя.
                user_input = input('Ваш перевод: ').strip()

                # Проверяем на завершающее слово
                if user_input.lower() == self.STOP_WORD.lower():
                    print('Спасибо за игру!')
                    break

                # Проверяем правильность перевода через метод Anki.
                is_correct = self._anki_game.check_translation(
                    word, user_input
                )

                if is_correct:
                    print('Верно!')
                else:
                    correct = self._anki_game.get_translation(word)
                    print(f'Неправильно, правильный ответ: {correct}')

            except ValueError as e:
                print(f'Ошибка: {e}')
                break
            except KeyboardInterrupt:
                print('\nИгра прервана пользователем.')
                break
            except EOFError:
                print('\nВвод завершён.')
                break

    def add_words(self) -> None:
        """
        Запускает интерактивный режим добавления новых слов.

        Пользователь вводит пары слово-перевод.
        Режим завершается при вводе STOP_WORD.
        """
        # Сообщаем пользователю о способе завершения.
        print(f'Для завершения ввода введите "{self.STOP_WORD}".')

        while True:
            try:
                # Запрашиваем слово.
                word_input = input('\nВведите слово: ').strip()

                # Проверяем на завершающее слово.
                if word_input.lower() == self.STOP_WORD.lower():
                    break

                # Запрашиваем перевод.
                translation_input = input('Введите перевод: ').strip()

                # Проверяем на завершающее слово (вместо перевода).
                if translation_input.lower() == self.STOP_WORD.lower():
                    break

                # Добавляем пару через метод Anki.
                self._anki_game.add_word(word_input, translation_input)
                print('Слово добавлено!')

            except ValueError as e:
                # Обрабатываем ошибки валидации от Anki.
                print(f'Ошибка: {e}')
            except KeyboardInterrupt:
                # Обрабатываем принудительное завершение.
                print('\nДобавление слов прервано.')
                break
            except EOFError:
                # Обрабатываем конец ввода.
                print('\nВвод завершён.')
                break

    def show_words(self) -> None:
        """
        Выводит все пары слов и переводов из коллекции.

        В начале показывает общее количество слов.
        Формат вывода: "слово - перевод" (по одной паре на строку).
        """
        # Используем магический метод __len__ для получения количества слов.
        total_words: int = len(self._anki_game)

        # Проверяем наличие слов.
        if not total_words:
            print('Коллекция слов пуста.')
            return

        # Выводим общее количество слов
        print(f'Всего слов в коллекции: {total_words}')
        # print('-' * 40)

        for word, translation in self._anki_game:
            print(f'{word} - {translation}')

    def train_until_mistake(self) -> None:
        """
        Запускает режим тренировки до первой ошибки.

        Пользователь должен переводить слова по порядку.
        Тренировка завершается при первой ошибке или вводе STOP_WORD.
        После завершения выводится статистика: время и счёт.
        """
        # Проверяем наличие слов перед началом тренировки.
        try:
            self._anki_game.get_random_word()
        except ValueError:
            print('Слов для тренировки нет. Добавьте слова через меню.')
            return

        # Запускаем сессию.
        self._anki_game.start_session()
        print('Тренировка до первой ошибки началась!')
        print(f'Для завершения введите "{self.STOP_WORD}".')

        try:
            while True:
                # Получаем случайное слово.
                word = self._anki_game.get_random_word()
                print(f'\nВаше слово для перевода: {word}')

                # Получаем ответ пользователя.
                user_input = input('Ваш перевод: ').strip()

                # Проверяем на завершающее слово.
                if user_input.lower() == self.STOP_WORD.lower():
                    print('Тренировка завершена пользователем.')
                    self._anki_game.end_session()
                    break

                # Проверяем правильность перевода.
                is_correct = self._anki_game.check_translation(
                    word, user_input
                )

                if is_correct:
                    print('Верно!')
                else:
                    print('Ошибка! Тренировка завершена.')
                    break

        except ValueError as e:
            print(f'Ошибка: {e}')
            # Сессия уже завершена в check_translation().
        except KeyboardInterrupt:
            print('\nТренировка прервана пользователем.')
            if self._anki_game._session_active:
                self._anki_game.end_session()
        except EOFError:
            print('\nВвод завершён.')
            if self._anki_game._session_active:
                self._anki_game.end_session()

        # Выводим статистику после завершения.
        stats: dict[str, float | int] = self._anki_game.last_session_stats
        print('\n' + '=' * 40)
        print('Статистика тренировки:')
        print(f'Правильных ответов: {stats["correct_answers"]}')
        print(f'Время игры: {stats["total_time"]:.2f} сек.')
        print('=' * 40)

    def find_translation(self) -> None:
        """
        Находит и выводит перевод для указанного слова.

        Запрашивает у пользователя слово для поиска.
        Проверяет наличие слова в словаре игры.
        Выводит перевод, если слово найдено, или сообщение об отсутствии.
        """
        word_input = input('\nВведите слово для поиска: ').strip()

        # Проверяем на завершающее слово.
        if word_input.lower() == self.STOP_WORD.lower():
            print('Поиск отменён.')
            return

        try:
            translation = self._anki_game.get_translation(word_input)
            print(f'Перевод слова "{word_input}": {translation}')
        except ValueError as e:
            print(f'Слово не найдено: {e}')

    def get_available_commands(self) -> list[tuple[Callable[..., None], str]]:
        """
        Возвращает доступные команды для меню.

        Фильтрует команды по условию видимости (предикату).

        Returns:
            list[tuple[Callable[..., None], str]]: Список кортежей
                (функция-обработчик, описание команды).
        """
        commands: list[tuple[Callable[..., None], str]] = []

        for func, description, is_visible in self._command_definition:
            if is_visible():
                commands.append((func, description))

        return commands

    def main_loop(self) -> None:
        """
        Запускает главный цикл пользовательского интерфейса.

        Отображает меню и обрабатывает выбор пользователя.
        Завершается при выборе пункта "Выход".
        """
        self._is_running = True

        while self._is_running:
            menu_choices: list[str] = []
            commands: dict[str, Callable[..., None]] = {}

            for i, (func, description) in enumerate(
                self.get_available_commands(), 1
            ):
                menu_choices.append(f'{i}. {description}')
                commands[str(i)] = func

            # Показываем меню
            print('Меню:\n' + '\n'.join(menu_choices))
            choice = input('Выберите пункт: ')

            if choice in commands:
                commands[choice]()
            else:
                print('Неверный пункт меню')
            print()
