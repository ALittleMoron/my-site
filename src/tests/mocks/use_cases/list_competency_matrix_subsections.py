from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import Subsection, Subsections
from app.core.use_cases import UseCase


@dataclass
class MockListSubsectionsUseCase(UseCase):
    subsections: list[Subsection] = field(default_factory=list)

    async def execute(self) -> Subsections:
        return Subsections(values=self.subsections)
