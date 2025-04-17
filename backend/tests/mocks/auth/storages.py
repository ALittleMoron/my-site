from dataclasses import dataclass, field

from core.users.exceptions import UserNotFoundError
from core.users.schemas import User
from db.storages.auth import AuthStorage


@dataclass(kw_only=True, slots=True)
class MockAuthStorage(AuthStorage):
    users: list[User] = field(default_factory=list)

    async def get_user_by_username(self, username: str) -> User:
        for user in self.users:
            if user.username == username:
                return user
        raise UserNotFoundError
