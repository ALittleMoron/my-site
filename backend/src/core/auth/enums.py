from core.enums import LabeledStrEnum


class RoleEnum(LabeledStrEnum):
    ANON = "anon", "Анонимный"
    USER = "user", "Пользователя"
    MODERATOR = "moderator", "Модератор"
    ADMIN = "admin", "Администратор"
