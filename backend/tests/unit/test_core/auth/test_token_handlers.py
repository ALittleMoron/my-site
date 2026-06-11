from core.auth.token_handlers import TokenHandler


class TestTokenHandler:
    def test_valid_payload_not_valid_payload_fields(self) -> None:
        payload_dict = {"password": "test", "field": "test"}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is False
        assert result.message == "Token payload is missing required fields: role, username."

    def test_valid_payload_username_not_str(self) -> None:
        payload_dict = {"username": 25, "role": "admin"}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is False
        assert result.message == "Token payload field `username` must be a string."

    def test_valid_payload_role_not_str(self) -> None:
        payload_dict = {"username": "test", "role": 25}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is False
        assert result.message == "Token payload field `role` must be a string."

    def test_valid_payload_role_not_in_role_enum(self) -> None:
        payload_dict = {"username": "test", "role": "TEST"}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is False
        assert result.message == "Token payload field `role` is not supported."

    def test_valid_payload(self) -> None:
        payload_dict = {"username": "test", "role": "admin"}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is True
        assert result.message == "Token payload is valid."

    def test_valid_payload_moderator_role(self) -> None:
        payload_dict = {"username": "test", "role": "moderator"}
        result = TokenHandler.validate_payload_dict(payload_dict)
        assert result.is_valid is True
        assert result.message == "Token payload is valid."
