import textwrap
from anki.anki import Anki


class TextUI:
    """
    Класс для взаимодействия с пользователем и отрисовки текстового интерфейса.

    Использует экземпляр класса Anki для игровой логики и управления словами.
    Реализует меню, игровой режим и управление коллекцией слов.
    """

    # Константа для завершения игры.
    STOP_WORD: str = 'СТОП'

    # Меню приложения.
    # dedent убирает отступы кода, чтобы меню выглядело ровно в консоли.
    # \ после ''' предотвращает появление лишней пустой строки в начале.
    MENU = textwrap.dedent('''\
        Меню:
        1. Начать игру
        2. Добавить слова
        3. Тренировка до первой ошибки
        4. Вывод всех слов
        5. Выход
        ''')

    def __init__(self, anki_game: Anki) -> None:
        """
        Инициализирует интерфейс с экземпляром игры Anki.

        Args:
            anki_game (Anki): Экземпляр класса Anki для игровой логики.

        Raises:
            ValueError: Если переданный аргумент не является экземпляром Anki.
        """

        # Сохраняем ссылку на экземпляр Anki для использования в методах.
        self._anki_game = anki_game

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
                print('\nИгра перрвана пользователем.')
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
        total_words = len(self._anki_game)

        # Проверяем наличие слов.
        if not total_words:
            print('Коллекция слов пуста.')
            return

        # Выводим общее количество слов
        print(f'Всего слов в коллекции: {total_words}')
        print('-' * 40)

        for word, translation in self._anki_game:
            print(f'{word} - {translation}')

    def train_until_mistake(self) -> None:
        """
        Заглушка для режима тренировки до первой ошибки.

        Данная функциональность ещё не реализована.
        """
        print('Данная функциональность ещё не реализована.')

    def main_loop(self) -> None:
        """
        Запускает главный цикл пользовательского интерфейса.

        Отображает меню и обрабатывает выбор пользователя.
        Завершается при выборе пункта "Выход".
        """
        while True:
            try:
                # Отрисовываем меню.
                print(self.MENU)

                # Получаем выбор пользователя.
                choice = input('Пункт меню: ').strip()

                # Обрабатываем выбор.
                if choice == '1':
                    # Начать игру.
                    self.start_game()
                elif choice == '2':
                    # Добавить слова.
                    self.add_words()
                elif choice == '3':
                    # Тренировка до первой ошибки (заглушка).
                    self.train_until_mistake()
                elif choice == '4':
                    # Вывод всех слов.
                    self.show_words()
                elif choice == '5':
                    # Выход.
                    print('Выход из программы.')
                    break
                else:
                    # Неверный выбор.
                    print('Неизвестный пункт меню.')

            except KeyboardInterrupt:
                # Обрабатываем принудительное завершение.
                print('\nПрограмма прервана пользователем.')
                break
            except EOFError:
                # Обрабатываем конец ввода.
                print('\nВвод завершён.')
                break
