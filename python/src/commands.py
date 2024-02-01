from abc import ABC, abstractmethod
import datetime
import sys
import requests

from presistence import BookmarkDatabase

presistence = BookmarkDatabase()


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        raise NotImplementedError("コマンドは必ずメソッドexecuteを実装してください")


class AddBookmarkCommand(Command):
    def execute(self, data, timestamp=None):
        data["date_added"] = timestamp or datetime.datetime.utcnow().isoformat()
        presistence.create(data)
        return True, None


class ListBookmarksCommand(Command):
    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self, data):
        return True, presistence.list(order_by=self.order_by)


class DeleteBookmarkCommand(Command):
    def execute(self, data):
        presistence.delete(data)
        return True, None


class EditBookmarkCommand(Command):
    def execute(self, data):
        presistence.edit(data["id"], data["update"])
        return True, None


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

        return True, bookmarks_imported
