from enum import StrEnum


class CompetencyMatrixWorkspaceSortEnum(StrEnum):
    GRADE = "grade"
    SECTION = "section"
    SUBSECTION = "subsection"
    NEWEST = "newest"
    OLDEST = "oldest"
    MISSING_FIELDS = "missingFields"
    DANGEROUS_PUBLISHED = "dangerousPublished"


class GradeEnum(StrEnum):
    JUNIOR = "Junior"
    JUNIOR_PLUS = "Junior+"
    MIDDLE = "Middle"
    MIDDLE_PLUS = "Middle+"
    SENIOR = "Senior"
