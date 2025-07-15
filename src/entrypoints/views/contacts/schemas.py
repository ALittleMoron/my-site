from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

from core.contacts.schemas import ContactMe
from entrypoints.api.schemas import CamelCaseSchema


class ContactMeRequest(CamelCaseSchema):
    name: Annotated[
        str | None,
        Field(
            description="Имя пользователя (можно полное по желанию).",
            examples=["Дмитрий Лунев"],
        ),
    ] = None
    email: Annotated[
        str | None,
        Field(
            description="Адрес электронной почты пользователя.",
            examples=["example@mail.ru"],
        ),
    ]
    telegram: Annotated[
        str | None,
        Field(
            description="Телеграм аккаунт для связи с пользователем",
            examples=["@alittlemoron"],
        ),
    ] = None
    message: Annotated[
        str,
        Field(
            min_length=1,
            max_length=10000,
            description="Сообщение для связи",
            examples=["Хочу ЗП 500к"],
        ),
    ]

    def is_valid(self) -> tuple[Literal[False], str] | tuple[Literal[True], None]:
        name_min_length, name_max_length = 1, 255
        email_min_length, email_max_length = 1, 255
        telegram_min_length, telegram_max_length = 2, 256
        if all(item is None for item in [self.name, self.email, self.telegram]):
            return False, "Нужно, чтобы хотя бы 1 поле было заполнено: имя, email или telegram"
        if self.name is not None and (name_max_length < len(self.name) < name_min_length):
            return False, "Имя пользователя имеет невалидную длину"
        if self.email is not None and (email_max_length < len(self.email) < email_min_length):
            return False, "email пользователя имеет невалидную длину"
        if self.telegram is not None and (
            telegram_max_length < len(self.telegram) < telegram_min_length
        ):
            return False, "Телеграм пользователя имеет невалидную длину"
        if self.telegram is not None:
            if self.telegram[0] != "@":
                self.telegram = "@" + self.telegram
            if len(self.telegram) > telegram_max_length:
                return (
                    False,
                    "Телеграм пользователя больше максимального из-за непроставленного знака @",
                )
        return True, None

    def to_schema(self, contact_me_id: UUID, user_ip: str) -> ContactMe:
        return ContactMe(
            id=contact_me_id,
            user_ip=user_ip,
            name=self.name,
            email=self.email,
            telegram=self.telegram,
            message=self.message,
        )
