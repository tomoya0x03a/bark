from database import DatabaseManager
from abc import ABC, abstractmethod
import datetime
import sys
import requests

db = DatabaseManager("bookmarks.db")


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        raise NotImplementedError("コマンドは必ずメソッドexecuteを実装してください")


class CreateBookMarksTableCommand(Command):
    def execute(self, data=None):
        db.create_table(
            "bookmarks",
            {
                "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
                "title": "TEXT NOT NULL",
                "url": "TEXT NOT NULL",
                "notes": "TEXT",
                "date_added": "TEXT NOT NULL",
            },
        )


class AddBookmarkCommand(Command):
    def execute(self, data, timestamp=None):
        data["date_added"] = timestamp or datetime.datetime.utcnow().isoformat()
        db.add("bookmarks", data)
        return "ブックマークを追加しました。"


class ListBookmarksCommand(Command):
    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self):
        return db.select("bookmarks", order_by=self.order_by).fetchall()


class DeleteBookmarkCommand(Command):
    def execute(self, data):
        db.delete("bookmarks", {"id": data})
        return "ブックマークを削除しました。"


class EditBookmarkCommand(Command):
    def execute(self, data):
        db.update(
            "bookmarks",
            data["update"],
            {
                "id": data["id"],
            },
        )
        return "ブックマークを編集しました。"


class QuitCommand(Command):
    def execute(self, data=None):
        sys.exit()


class ImportGitHubStarsCommand(Command):
    def _extract_bookmark_info(self, repo):
        return {
            "title": repo["name"],
            "url": repo["html_url"],
            "notes": repo["description"],
        }

    def execute(self, data):
        bookmarks_imported = 0

        github_username = data["github_username"]
        next_page_of_results = f"https://api.github.com/users/{github_username}/starred"

        while next_page_of_results:
            stars_response = requests.get(
                next_page_of_results,
                headers={"Accept": "application/vnd.github.v3.start+json"},
            )
            next_page_of_results = stars_response.links.get("next", {}).get("url")

            for repo_info in stars_response.json():
                if data["preserve_timestamps"]:
                    timestamp = datetime.datetime.strptime(
                        repo_info["updated_at"],
                        "%Y-%m-%dT%H:%M:%SZ",
                    )
                else:
                    timestamp = None

                bookmarks_imported += 1
                AddBookmarkCommand().execute(
                    self._extract_bookmark_info(repo_info), timestamp=timestamp
                )

        return f"{bookmarks_imported}個のブックマークをインポートしました。"
