from dataclasses import dataclass
from itertools import groupby
from typing import Any

from core.competency_matrix.enums import GradeEnum
from core.competency_matrix.schemas import CompetencyMatrixItems, Sheets, CompetencyMatrixItem


@dataclass(kw_only=True, frozen=True, slots=True)
class CompetencyMatrixContextConverter:
    def from_competency_matrix_sheets(self, sheets: Sheets) -> dict[str, Any]:
        return {"sheets": sheets.values}

    def context_from_competency_matrix_item(
        self,
        item: CompetencyMatrixItem,
    ) -> dict[str, Any]:
        return {
            "item_id": item.id,
            "question": item.question,
            "answer": item.answer,
            "interview_expected_answer": item.interview_expected_answer,
            "sheet": item.sheet,
            "grade": item.grade,
            "section": item.section,
            "subsection": item.subsection,
            "resources": [
                {
                    "id": resource.id,
                    "name": resource.name,
                    "url": resource.url,
                    "context": resource.context,
                }
                for resource in item.resources
            ],
        }

    def context_from_competency_matrix_items(
        self,
        sheet: str,
        items: CompetencyMatrixItems,
    ) -> dict[str, Any]:
        result_dict: dict[str, Any] = {"sheet": sheet}
        sections = []
        for section, section_items in groupby(items, key=lambda item: item.section):
            subsections = []
            for subsection, subsection_items in groupby(
                section_items,
                key=lambda item: item.subsection,
            ):
                grades_list = list(subsection_items)
                grades_dict = [
                    {
                        "grade": grade.value,
                        "items": [
                            {"id": item.id, "question": item.question}
                            for item in filter(lambda item: item.grade == grade, grades_list)
                        ],
                    }
                    for grade in GradeEnum
                ]
                subsections.append({"subsection": subsection, "grades": grades_dict})
            sections.append({"section": section, "subsections": subsections})
        result_dict["sections"] = sections
        return result_dict
