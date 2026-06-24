from httpx import codes

from tests.test_cases import ApiTestCase


class TestI18nApi(ApiTestCase):
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
        assert body["messages"]["shell.nav.adminPanel"] == "Админ-панель"
        assert body["messages"]["adminPanel.title"] == "Админ-панель"
        assert body["messages"]["enum.publishStatus.Draft"] == "Черновик"
        assert body["messages"]["enum.grade.JuniorPlus"] == "Junior+"
        assert body["messages"]["auth.login.restrictedAccessWarning.title"] == (
            "Пока только для модераторов и администраторов"
        )

    def test_get_english_bundle(self) -> None:
        response = self.api.get_i18n_bundle(language="en")

        assert response.status_code == codes.OK, response.content
        body = response.json()
        assert body["language"] == "en"
        assert body["messages"]["shell.nav.about"] == "About"
        assert body["messages"]["shell.nav.adminPanel"] == "Admin panel"
        assert body["messages"]["adminPanel.title"] == "Admin panel"
        assert body["messages"]["enum.publishStatus.Draft"] == "Draft"
        assert body["messages"]["enum.grade.JuniorPlus"] == "Junior+"
        assert (
            body["messages"]["auth.login.restrictedAccessWarning.title"]
            == "Moderators and admins only for now"
        )

    def test_unknown_bundle_language_is_rejected(self) -> None:
        response = self.api.get_i18n_bundle(language="de")

        assert response.status_code == codes.BAD_REQUEST
