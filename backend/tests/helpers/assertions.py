from typing import Any, cast

from httpx import Response

RESUME_RESPONSE_ALLOWED_NULL_KEYS = frozenset({"startDate", "endDate", "issuedOn", "expiresOn"})
RESUME_LOCALIZED_FIELD_SUFFIXES = ("Ru", "En")


class AssertsHelper:
    def equals(self, actual: object, expected: object) -> None:
        assert actual == expected

    def status(self, response: Response, expected_status: int) -> None:
        assert response.status_code == expected_status, response.content

    def json(self, response: Response, expected_status: int | None = None) -> Any:
        if expected_status is not None:
            self.status(response=response, expected_status=expected_status)
        return response.json()

    def json_body(self, response: Response, expected_status: int, expected_body: object) -> None:
        self.equals(
            actual=self.json(response=response, expected_status=expected_status),
            expected=expected_body,
        )

    def error_message(
        self,
        response: Response,
        expected_status: int,
        expected_message: str,
    ) -> dict[str, Any]:
        body = cast("dict[str, Any]", self.json(response=response, expected_status=expected_status))
        assert body["message"] == expected_message
        return body

    def resume_response_nulls_are_dates_only(
        self,
        *,
        value: object,
        key: str | None = None,
    ) -> None:
        if value is None:
            assert key in RESUME_RESPONSE_ALLOWED_NULL_KEYS
            return
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                self.resume_response_nulls_are_dates_only(value=child_value, key=child_key)
            return
        if isinstance(value, list):
            for item in value:
                self.resume_response_nulls_are_dates_only(value=item, key=key)

    def resume_response_has_no_localized_field_names(self, *, value: object) -> None:
        if isinstance(value, dict):
            for key, child_value in value.items():
                assert not key.endswith(RESUME_LOCALIZED_FIELD_SUFFIXES), key
                self.resume_response_has_no_localized_field_names(value=child_value)
            return
        if isinstance(value, list):
            for item in value:
                self.resume_response_has_no_localized_field_names(value=item)

    def resume_response_contract(self, *, value: object) -> None:
        self.resume_response_has_no_localized_field_names(value=value)
        self.resume_response_nulls_are_dates_only(value=value)
