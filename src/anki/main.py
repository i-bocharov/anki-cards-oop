from anki.anki import Anki
from anki.loader import TextFileLoader
from anki.ui import TextUI


def main():
    loader = TextFileLoader()

    anki = Anki(words=loader.load_words())

    ui = TextUI(anki)
    ui.main_loop()

    loader.save_words()


if __name__ == "__main__":
    main()
