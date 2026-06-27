from core.enums import StrEnum


class ManagedAccountActionEnum(StrEnum):
    UPDATE_ROLE = "updateRole"
    UPDATE_PASSWORD = "updatePassword"  # noqa: S105
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    DELETE = "delete"
