from dataclasses import dataclass, field

from app.core.competency_matrix.schemas import Subsection, Subsections, ListSubsectionsParams
from app.core.use_cases import UseCase


@dataclass
class MockListSubsectionsUseCase(UseCase):
    subsections: list[Subsection] = field(default_factory=list)
    params: ListSubsectionsParams | None = None

    async def execute(self, params: ListSubsectionsParams) -> Subsections:
        self.params = params
        return Subsections(values=self.subsections)
