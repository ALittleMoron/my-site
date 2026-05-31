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
        title_ru: str = "Заметка",
        title_en: str = "Note",
        content_ru: str = "Содержимое заметки",
        content_en: str = "Note content",
        slug: str = "note",
        folder_ru: str = "Общее",
        folder_en: str = "General",
        publish_status: str = "Draft",
        tag_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        return {
            "slug": slug,
            "publishStatus": publish_status,
            "tagIds": tag_ids or [],
            "translations": {
                "ru": {"title": title_ru, "content": content_ru, "folder": folder_ru},
                "en": {"title": title_en, "content": content_en, "folder": folder_en},
            },
        }

    @classmethod
    def tag_request(
        cls,
        name_ru: str = "Питон",
        name_en: str = "Python",
        slug: str = "python",
    ) -> dict[str, Any]:
        return {
            "slug": slug,
            "translations": {
                "ru": {"name": name_ru},
                "en": {"name": name_en},
            },
        }
