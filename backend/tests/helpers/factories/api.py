from typing import Any


class ApiFactoryHelper:
    @classmethod
    def contact_me_request(
        cls,
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> dict[str, Any]:
        return {
            "name": name,
            "email": email,
            "telegram": telegram,
            "message": message,
        }

    @classmethod
    def login_request(cls, username: str = "TEST", password: str | None = None) -> dict[str, Any]:
        return {"username": username, "password": password or "TEST"}

    @classmethod
    def note_request(
        cls,
        title: str = "Note",
        content: str = "Note content",
        slug: str = "note",
        folder: str = "General",
        publish_status: str = "Draft",
        tag_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        return {
            "title": title,
            "content": content,
            "slug": slug,
            "folder": folder,
            "publishStatus": publish_status,
            "tagIds": tag_ids or [],
        }

    @classmethod
    def tag_request(
        cls,
        name: str = "Python",
        slug: str = "python",
    ) -> dict[str, Any]:
        return {"name": name, "slug": slug}
