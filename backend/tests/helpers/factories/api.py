from typing import Any


class ApiFactoryHelper:
    @classmethod
    def contact_me_request(
        cls,
        name: str | None = None,
        email: str | None = None,
        telegram: str | None = None,
        message: str = "Message",
    ) -> dict[str, Any]:
        return {
            "name": name,
            "email": email,
            "telegram": telegram,
            "message": message,
        }

    @classmethod
    def login_request(cls, username: str = "TEST", password: str | None = None) -> dict[str, Any]:
        return {"username": username, "password": password or "TEST"}

    @classmethod
    def article_request(
        cls,
        title_ru: str = "Статья",
        title_en: str = "Article",
        content_ru: str = "Содержимое статьи",
        content_en: str = "Article content",
        slug: str = "article",
        folder_ru: str = "Общее",
        folder_en: str = "General",
        publish_status: str = "Draft",
        metadata: dict[str, Any] | None = None,
        tag_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        return {
            "slug": slug,
            "publishStatus": publish_status,
            "tagIds": tag_ids or [],
            "metadata": metadata
            if metadata is not None
            else {
                "seoTitleRu": "SEO статья",
                "seoTitleEn": "SEO article",
                "seoDescriptionRu": "Описание для выдачи",
                "seoDescriptionEn": "Search result description",
                "coverImageUrl": "https://example.com/cover.jpg",
                "coverImageAltRu": "Обложка статьи",
                "coverImageAltEn": "Article cover",
            },
            "translations": {
                "ru": {"title": title_ru, "content": content_ru, "folder": folder_ru},
                "en": {"title": title_en, "content": content_en, "folder": folder_en},
            },
        }

    @classmethod
    def tag_request(
        cls,
        name_ru: str = "Питон",
        name_en: str = "Python",
        slug: str = "python",
    ) -> dict[str, Any]:
        return {
            "slug": slug,
            "translations": {
                "ru": {"name": name_ru},
                "en": {"name": name_en},
            },
        }

    @classmethod
    def competency_matrix_item_request(
        cls,
        slug: str = "question-1",
        question_ru: str = "вопрос 1",
        question_en: str = "question 1",
        answer_ru: str = "ответ 1",
        answer_en: str = "answer 1",
        interview_expected_answer_ru: str = "ожидаемый ответ 1",
        interview_expected_answer_en: str = "interview expected answer 1",
        sheet_key: str = "python",
        sheet_ru: str = "Питон",
        sheet_en: str = "Python",
        grade: str | None = "Junior",
        section_ru: str = "Основы",
        section_en: str = "Basics",
        subsection_ru: str = "Функции",
        subsection_en: str = "Functions",
        publish_status: str = "Draft",
        resources: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return {
            "slug": slug,
            "sheetKey": sheet_key,
            "grade": grade,
            "publishStatus": publish_status,
            "translations": {
                "ru": {
                    "question": question_ru,
                    "answer": answer_ru,
                    "interviewExpectedAnswer": interview_expected_answer_ru,
                    "sheet": sheet_ru,
                    "section": section_ru,
                    "subsection": subsection_ru,
                },
                "en": {
                    "question": question_en,
                    "answer": answer_en,
                    "interviewExpectedAnswer": interview_expected_answer_en,
                    "sheet": sheet_en,
                    "section": section_en,
                    "subsection": subsection_en,
                },
            },
            "resources": resources or [],
        }

    @classmethod
    def question_suggestion_request(cls, question: str = "What is PEP 8?") -> dict[str, Any]:
        return {"question": question}

    @classmethod
    def existing_matrix_resource_attachment_request(
        cls,
        resource_id: int = 1,
        context_ru: str = "контекст ресурса",
        context_en: str = "resource context",
    ) -> dict[str, Any]:
        return {
            "resourceId": resource_id,
            "translations": {
                "ru": {"context": context_ru},
                "en": {"context": context_en},
            },
        }

    @classmethod
    def new_matrix_resource_attachment_request(
        cls,
        name_ru: str = "ресурс",
        name_en: str = "resource",
        url: str = "http://example.com",
        context_ru: str = "контекст ресурса",
        context_en: str = "resource context",
    ) -> dict[str, Any]:
        return {
            "resource": {
                "url": url,
                "translations": {
                    "ru": {"name": name_ru},
                    "en": {"name": name_en},
                },
            },
            "translations": {
                "ru": {"context": context_ru},
                "en": {"context": context_en},
            },
        }
