from dataclasses import dataclass
from itertools import groupby
from typing import Any

from core.competency_matrix.schemas import CompetencyMatrixItems, Sheets, CompetencyMatrixItem


@dataclass(kw_only=True, frozen=True, slots=True)
class CompetencyMatrixContextConverter:
    def from_competency_matrix_sheets(self, sheets: Sheets) -> dict[str, Any]:
        return {"sheets": sheets.values}

    def from_competency_matrix_item(
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

    def from_competency_matrix_items(
        self,
        sheet: str,
        items: CompetencyMatrixItems,
    ) -> dict[str, Any]:
        return {
            "sheet": sheet,
            "sections": [
                {
                    "section": section,
                    "subsections": [
                        {
                            "subsection": subsection,
                            "grades": [
                                {
                                    "grade": grade,
                                    "items": [
                                        {"id": item.id, "question": item.question}
                                        for item in grade_items
                                    ],
                                }
                                # FIXME: add grade enum + make sure all grades will be in dict
                                for grade, grade_items in groupby(
                                    subsection_items,
                                    key=lambda item: item.grade,
                                )
                            ],
                        }
                        for subsection, subsection_items in groupby(
                            section_items,
                            key=lambda item: item.subsection,
                        )
                    ],
                }
                for section, section_items in groupby(items, key=lambda item: item.section)
            ],
        }
