from datetime import UTC, datetime

import pytest_asyncio
from httpx import codes

from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from core.competency_matrix.enums import CompetencyMatrixWorkspaceSortEnum, GradeEnum
from core.competency_matrix.schemas import (
    CompetencyMatrixFilterOptions,
    CompetencyMatrixFilterSectionOption,
    CompetencyMatrixFilterSheetOption,
    CompetencyMatrixMissingFieldEnum,
    CompetencyMatrixWorkspace,
    CompetencyMatrixWorkspaceFilters,
    CompetencyMatrixWorkspaceItem,
    CompetencyMatrixWorkspaceSummary,
)
from core.enums import PublishStatusEnum
from core.i18n.enums import LanguageEnum
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestWorkspaceItemsAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.authentication_use_case = await self.container.get_auth_use_case()
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_workspace_requires_sort(self) -> None:
        response = self.api.get_admin_competency_matrix_workspace_items(sort=None)

        assert response.status_code == codes.BAD_REQUEST
        self.use_case.list_workspace_items.assert_not_called()

    def test_moderator_can_list_workspace_items_with_filters(self) -> None:
        self.authentication_use_case.authenticate.return_value = JwtUser(
            username="moderator",
            role=RoleEnum.MODERATOR,
        )
        published_at = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.use_case.list_workspace_items.return_value = CompetencyMatrixWorkspace(
            total_count=1,
            total_pages=1,
            summary=CompetencyMatrixWorkspaceSummary(
                total=1,
                draft=0,
                missing_draft=0,
                dangerous_published=1,
                ready_published=0,
            ),
            values=[
                CompetencyMatrixWorkspaceItem(
                    id=self.factory.core.int_id(7),
                    slug="python-functions",
                    question="How do functions work?",
                    sheet_key="python",
                    sheet="Python",
                    grade=GradeEnum.JUNIOR,
                    section="Basics",
                    subsection="Functions",
                    publish_status=PublishStatusEnum.PUBLISHED,
                    published_at=published_at,
                    missing_fields=(CompetencyMatrixMissingFieldEnum.ANSWER_EN,),
                ),
            ],
        )

        response = self.api.get_admin_competency_matrix_workspace_items(
            page=1,
            page_size=20,
            language="en",
            sort="dangerousPublished",
            sheet_keys=["python", "sql"],
            grades=["Junior"],
            sections=["Basics"],
            subsections=["Functions"],
            publish_statuses=["Published"],
            search_query="functions",
            published_from="2026-01-01",
            published_to="2026-01-31",
            has_missing_fields=True,
        )

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "totalCount": 1,
            "totalPages": 1,
            "summary": {
                "total": 1,
                "draft": 0,
                "missingDraft": 0,
                "dangerousPublished": 1,
                "readyPublished": 0,
            },
            "items": [
                {
                    "id": 7,
                    "slug": "python-functions",
                    "question": "How do functions work?",
                    "sheetKey": "python",
                    "sheet": "Python",
                    "grade": "Junior",
                    "section": "Basics",
                    "subsection": "Functions",
                    "publishStatus": "Published",
                    "publishedAt": "2026-01-02T03:04:05+00:00",
                    "missingFields": ["answerEn"],
                },
            ],
        }
        self.use_case.list_workspace_items.assert_called_once_with(
            filters=CompetencyMatrixWorkspaceFilters(
                page=1,
                page_size=20,
                language=LanguageEnum.EN,
                sort=CompetencyMatrixWorkspaceSortEnum.DANGEROUS_PUBLISHED,
                search_query="functions",
                sheet_keys=("python", "sql"),
                grades=(GradeEnum.JUNIOR,),
                sections=("Basics",),
                subsections=("Functions",),
                publish_statuses=(PublishStatusEnum.PUBLISHED,),
                published_from=datetime(2026, 1, 1, tzinfo=UTC).date(),
                published_to=datetime(2026, 1, 31, tzinfo=UTC).date(),
                has_missing_fields=True,
            ),
        )

    def test_lists_workspace_filter_options(self) -> None:
        self.use_case.list_workspace_filter_options.return_value = CompetencyMatrixFilterOptions(
            sheets=[
                CompetencyMatrixFilterSheetOption(
                    key="python",
                    label="Python",
                    sections=[
                        CompetencyMatrixFilterSectionOption(
                            label="Basics",
                            subsections=["Functions"],
                        ),
                    ],
                ),
            ],
            grades=[GradeEnum.JUNIOR],
            sections=["Basics"],
            subsections=["Functions"],
            publish_statuses=[PublishStatusEnum.DRAFT, PublishStatusEnum.PUBLISHED],
        )

        response = self.api.get_admin_competency_matrix_workspace_filter_options(language="en")

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "sheets": [
                {
                    "key": "python",
                    "label": "Python",
                    "sections": [{"label": "Basics", "subsections": ["Functions"]}],
                },
            ],
            "grades": ["Junior"],
            "sections": ["Basics"],
            "subsections": ["Functions"],
            "publishStatuses": ["Draft", "Published"],
        }
        self.use_case.list_workspace_filter_options.assert_called_once_with(
            language=LanguageEnum.EN,
        )
