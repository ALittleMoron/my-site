from enum import StrEnum
from typing import Self


class LabeledStrEnum(StrEnum):
    label: str

    def __new__(cls, value: str, label: str = "") -> Self:
        member = str.__new__(cls, value)
        member._value_ = value
        member.label = label
        return member


class PublishStatusEnum(LabeledStrEnum):
    DRAFT = "Draft", "Черновик"
    PUBLISHED = "Published", "Опубликовано"
