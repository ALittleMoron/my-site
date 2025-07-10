from enum import StrEnum


class StatusEnum(StrEnum):
    DRAFT = "Draft"
    PUBLISHED = "Published"


class GradeEnum(StrEnum):
    JUNIOR = "Junior"
    JUNIOR_PLUS = "Junior+"
    MIDDLE = "Middle"
    MIDDLE_PLUS = "Middle+"
    SENIOR = "Senior"
