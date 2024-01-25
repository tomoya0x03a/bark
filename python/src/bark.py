import commands
from collections import OrderDict


class Option:
    def __init__(self, name, command, prep_call=None):
        self.name = name
        self.command = command
        self.prep_call = prep_call

    def _handle_message(self, message):
        if isinstance(message, list):
            print_bookmarks(message)
        else:
            print(message)

    def choose(self):
        data = self.prep_call() if self.prep_call else None
        message = self.command.execute(data) if data else self.command.execute()
        self._handle_message(message)

    def __str__(self):
        return self.name


def print_options(options):
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")


if __name__ == "__main__":
    commands.CreateBookMarksTableCommand().execute

    options = OrderDict(
        {
            "A": Option(
                "追加",
                commands.AddBookmarkCommand(),
                prep_call=get_new_bookmark_data,
            ),
            "B": Option(
                "登録順にリスト",
                commands.ListBookmarksCommand(),
            ),
            "T": Option(
                "タイトル順にリスト",
                commands.ListBookmarksCommand(order_by="title"),
            ),
            "D": Option(
                "削除",
                commands.DeleteBookmarkCommand(),
                prep_call=get_bookmark_id_for_deletion,
            ),
            "Q": Option(
                "終了",
                commands.QuitCommand(),
            ),
        }
    )

    print_options(options)
