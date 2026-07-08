from datetime import UTC, datetime
from unittest.mock import Mock

from core.auth.schemas import AuthSessionCleanupParams, AuthSessionCleanupResult
from core.auth.storages import AuthSessionStorage
from core.auth.use_cases import AuthSessionCleanupUseCase
from tests.test_cases import TestCase


class TestAuthSessionCleanupUseCase(TestCase):
    async def test_prune_expired_sessions_deletes_sessions_expired_at_current_datetime(
        self,
    ) -> None:
        current_datetime = datetime(2026, 7, 8, 11, 30, tzinfo=UTC)
        auth_session_storage = Mock(spec=AuthSessionStorage)
        auth_session_storage.delete_expired_sessions.return_value = 3
        use_case = AuthSessionCleanupUseCase(auth_session_storage=auth_session_storage)

        result = await use_case.prune_expired_sessions(
            params=AuthSessionCleanupParams(current_datetime=current_datetime),
        )

        assert result == AuthSessionCleanupResult(deleted_count=3)
        assert result.as_dict() == {"deletedCount": 3}
        auth_session_storage.delete_expired_sessions.assert_called_once_with(
            expires_at=current_datetime,
        )
