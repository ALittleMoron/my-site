from unittest.mock import ANY

import pytest_asyncio
from httpx import codes

from core.competency_matrix.enums import GradeEnum
from core.enums import PublishStatusEnum
from tests.unit.fixtures import ApiFixture, ContainerFixture, FactoryFixture


class TestCreateItemAPI(ContainerFixture, ApiFixture, FactoryFixture):
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self) -> None:
        self.use_case = await self.container.get_competency_matrix_use_case()

    def test_create_item(self) -> None:
        self.use_case.create_item.return_value = self.factory.core.competency_matrix_item(
            item_id=1,
            question_ru="вопрос 1",
            question_en="question 1",
            answer_ru="ответ 1",
            answer_en="answer 1",
            interview_expected_answer_ru="ожидаемый ответ 1",
            interview_expected_answer_en="interview expected answer 1",
            sheet_key="python",
            sheet_ru="Питон",
            sheet_en="Python",
            grade=GradeEnum.JUNIOR,
            section_ru="Основы",
            section_en="Basics",
            subsection_ru="Функции",
            subsection_en="Functions",
            publish_status=PublishStatusEnum.DRAFT,
            resources=[
                self.factory.core.attached_external_resource(
                    resource_id=1,
                    name_ru="ресурс 1",
                    name_en="resource 1",
                    url="http://example.com",
                    context_ru="контекст ресурса 1",
                    context_en="resource context 1",
                ),
            ],
        )
        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(
                resources=[
                    self.factory.api.existing_matrix_resource_attachment_request(
                        resource_id=1,
                        context_ru="контекст ресурса 1",
                        context_en="resource context 1",
                    ),
                    self.factory.api.existing_matrix_resource_attachment_request(
                        resource_id=2,
                        context_ru="контекст ресурса 2",
                        context_en="resource context 2",
                    ),
                    self.factory.api.new_matrix_resource_attachment_request(
                        name_ru="ресурс 1",
                        name_en="resource 1",
                        url="http://example.com",
                        context_ru="контекст ресурса 3",
                        context_en="resource context 3",
                    ),
                ],
            ),
            language="en",
        )
        self.use_case.create_item.assert_called_once_with(
            params=self.factory.core.competency_matrix_item_create_params(
                item_id=1,
                question_ru="вопрос 1",
                question_en="question 1",
                answer_ru="ответ 1",
                answer_en="answer 1",
                interview_expected_answer_ru="ожидаемый ответ 1",
                interview_expected_answer_en="interview expected answer 1",
                sheet_key="python",
                sheet_ru="Питон",
                sheet_en="Python",
                grade=GradeEnum.JUNIOR,
                section_ru="Основы",
                section_en="Basics",
                subsection_ru="Функции",
                subsection_en="Functions",
                publish_status=PublishStatusEnum.DRAFT,
                resources=[
                    self.factory.core.existing_external_resource_attachment(
                        resource_id=1,
                        context_ru="контекст ресурса 1",
                        context_en="resource context 1",
                    ),
                    self.factory.core.existing_external_resource_attachment(
                        resource_id=2,
                        context_ru="контекст ресурса 2",
                        context_en="resource context 2",
                    ),
                    self.factory.core.new_external_resource_attachment(
                        resource_id=ANY,
                        name_ru="ресурс 1",
                        name_en="resource 1",
                        url="http://example.com",
                        context_ru="контекст ресурса 3",
                        context_en="resource context 3",
                    ),
                ],
            ),
        )
        assert response.status_code == codes.CREATED, response.json()
        assert response.json() == {
            "id": 1,
            "question": "question 1",
            "answer": "answer 1",
            "interviewExpectedAnswer": "interview expected answer 1",
            "sheetKey": "python",
            "sheet": "Python",
            "grade": "Junior",
            "section": "Basics",
            "subsection": "Functions",
            "publishStatus": PublishStatusEnum.DRAFT.value,
            "translations": {
                "ru": {
                    "question": "вопрос 1",
                    "answer": "ответ 1",
                    "interviewExpectedAnswer": "ожидаемый ответ 1",
                    "sheet": "Питон",
                    "section": "Основы",
                    "subsection": "Функции",
                },
                "en": {
                    "question": "question 1",
                    "answer": "answer 1",
                    "interviewExpectedAnswer": "interview expected answer 1",
                    "sheet": "Python",
                    "section": "Basics",
                    "subsection": "Functions",
                },
            },
            "resources": [
                {
                    "id": ANY,
                    "name": "resource 1",
                    "url": "http://example.com",
                    "context": "resource context 1",
                    "translations": {
                        "ru": {"name": "ресурс 1", "context": "контекст ресурса 1"},
                        "en": {"name": "resource 1", "context": "resource context 1"},
                    },
                },
            ],
        }

    def test_create_item_rejects_resource_attachment_with_resource_id_and_resource(self) -> None:
        data = self.factory.api.competency_matrix_item_request(
            resources=[
                {
                    "resourceId": 1,
                    "resource": {
                        "url": "http://example.com",
                        "translations": {
                            "ru": {"name": "ресурс 1"},
                            "en": {"name": "resource 1"},
                        },
                    },
                    "translations": {
                        "ru": {"context": "контекст ресурса"},
                        "en": {"context": "resource context"},
                    },
                },
            ],
        )
        response = self.api.post_create_item(data=data)
        assert response.status_code == codes.BAD_REQUEST, response.json()
        self.use_case.create_item.assert_not_called()

    def test_create_item_requires_existing_resource_context_translations(self) -> None:
        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(
                resources=[{"resourceId": 1}],
            ),
        )
        assert response.status_code == codes.BAD_REQUEST, response.json()
        self.use_case.create_item.assert_not_called()

    def test_create_item_requires_new_resource_context_translations(self) -> None:
        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(
                resources=[
                    {
                        "resource": {
                            "url": "http://example.com",
                            "translations": {
                                "ru": {"name": "ресурс 1"},
                                "en": {"name": "resource 1"},
                            },
                        },
                    },
                ],
            ),
        )
        assert response.status_code == codes.BAD_REQUEST, response.json()
        self.use_case.create_item.assert_not_called()

    def test_create_item_requires_explicit_language(self) -> None:
        response = self.api.post_create_item(
            data=self.factory.api.competency_matrix_item_request(),
            language=None,
        )
        assert response.status_code == codes.BAD_REQUEST, response.json()
        self.use_case.create_item.assert_not_called()
