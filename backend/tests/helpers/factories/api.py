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
