from unittest.mock import Mock

import pytest

from core.competency_matrix.services import QuestionSuggestionLimiter
from core.competency_matrix.storages import CompetencyMatrixStorage
from core.competency_matrix.use_cases import CompetencyMatrixUseCase
from tests.unit.fixtures import FactoryFixture


class TestCompetencyMatrixUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.question_suggestion_limiter = Mock(spec=QuestionSuggestionLimiter)
        self.use_case = CompetencyMatrixUseCase(
            storage=self.storage,
            question_suggestion_limiter=self.question_suggestion_limiter,
        )

    async def test_list_sheets(self) -> None:
        self.storage.list_sheets.return_value = self.factory.core.sheets(values=["Python", "SQL"])
        sheets = await self.use_case.list_sheets()
        assert sheets == self.factory.core.sheets(values=["Python", "SQL"])
