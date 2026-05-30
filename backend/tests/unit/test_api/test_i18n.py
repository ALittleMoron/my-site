from httpx import codes

from tests.unit.fixtures import ApiFixture


class TestI18nApi(ApiFixture):
    def test_list_languages(self) -> None:
        response = self.api.get_i18n_languages()

        assert response.status_code == codes.OK, response.content
        assert response.json() == {
            "defaultLanguage": "ru",
            "languages": [
                {"code": "ru", "label": "Русский"},
                {"code": "en", "label": "English"},
            ],
        }

    def test_get_russian_bundle(self) -> None:
        response = self.api.get_i18n_bundle(language="ru")

        assert response.status_code == codes.OK, response.content
        body = response.json()
        assert body["language"] == "ru"
        assert body["messages"]["shell.nav.about"] == "Обо мне"
        assert body["messages"]["enum.publishStatus.Draft"] == "Черновик"
        assert body["messages"]["enum.grade.JuniorPlus"] == "Junior+"

    def test_get_english_bundle(self) -> None:
        response = self.api.get_i18n_bundle(language="en")

        assert response.status_code == codes.OK, response.content
        body = response.json()
        assert body["language"] == "en"
        assert body["messages"]["shell.nav.about"] == "About"
        assert body["messages"]["enum.publishStatus.Draft"] == "Draft"
        assert body["messages"]["enum.grade.JuniorPlus"] == "Junior+"

    def test_unknown_bundle_language_is_rejected(self) -> None:
        response = self.api.get_i18n_bundle(language="de")

        assert response.status_code == codes.BAD_REQUEST
