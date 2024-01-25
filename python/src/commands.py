from database import DatabaseManager
import datetime
import sys

db = DatabaseManager("bookmarks.db")


class CreateBookMarksTableCommand:
    def execute(self):
        db.create_table(
            "bookmarks",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "title": "TEXT NOT NULL",
                "url": "TEXT NOT NULL",
                "memo": "TEXT",
                "date_added": "TEXT NOT NULL",
            },
        )


class AddBookmarkCommand:
    def execute(self, data):
        data["date_added"] = datetime.datetime.utcnow().isformat()
        db.add("bookmarks", data)
        return "ブックマークを追加しました。"


class ListBookmarksCommand:
    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self):
        db.select(self, "bookmarks", order_by=self.order_by).fetchall()


class DeleteBookmarkCommand:
    def execute(self, data):
        db.delete(self, "bookmarks", {"id": data})
        return "ブックマークを削除しました。"


class QuitCommand:
    def execute(self):
        sys.exit()