from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.ioc.prodivers.database_provider import DatabaseProvider
from infra.post_commit_actions import PostCommitActions
from infra.postgresql import meta
from infra.postgresql.transactions import DatabaseTransactionState


class SessionContextManager:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, *_args: object) -> None:
        return None


class SessionFactory:
    def __init__(self, *, session: AsyncSession) -> None:
        self.session = session

    def __call__(self) -> SessionContextManager:
        return SessionContextManager(session=self.session)


class TestDatabasePostCommitActions:
    async def test_runs_actions_after_successful_commit(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        events: list[str] = []
        session = AsyncMock(spec=AsyncSession)
        session.commit.side_effect = lambda: events.append("commit")
        session_factory = cast(
            "async_sessionmaker[AsyncSession]",
            SessionFactory(session=session),
        )
        monkeypatch.setattr(meta, "sessionmaker", session_factory)
        action = AsyncMock(side_effect=lambda: events.append("post_commit"))
        post_commit_actions = PostCommitActions(actions=[action])
        provider = DatabaseProvider()
        generator = provider.provide_async_session(
            transaction_state=DatabaseTransactionState(rollback_required=False),
            post_commit_actions=post_commit_actions,
        )

        assert await anext(generator) is session
        with pytest.raises(StopAsyncIteration):
            await generator.asend(None)

        assert events == ["commit", "post_commit"]
        action.assert_awaited_once_with()

    async def test_skips_actions_after_rollback(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        session = AsyncMock(spec=AsyncSession)
        session_factory = cast(
            "async_sessionmaker[AsyncSession]",
            SessionFactory(session=session),
        )
        monkeypatch.setattr(meta, "sessionmaker", session_factory)
        action = AsyncMock()
        provider = DatabaseProvider()
        generator = provider.provide_async_session(
            transaction_state=DatabaseTransactionState(rollback_required=True),
            post_commit_actions=PostCommitActions(actions=[action]),
        )

        assert await anext(generator) is session
        with pytest.raises(StopAsyncIteration):
            await generator.asend(None)

        session.rollback.assert_awaited_once_with()
        session.commit.assert_not_awaited()
        action.assert_not_awaited()

    async def test_skips_actions_when_commit_fails(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        error_message = "commit failed"
        session = AsyncMock(spec=AsyncSession)
        session.commit.side_effect = RuntimeError(error_message)
        session_factory = cast(
            "async_sessionmaker[AsyncSession]",
            SessionFactory(session=session),
        )
        monkeypatch.setattr(meta, "sessionmaker", session_factory)
        action = AsyncMock()
        provider = DatabaseProvider()
        generator = provider.provide_async_session(
            transaction_state=DatabaseTransactionState(rollback_required=False),
            post_commit_actions=PostCommitActions(actions=[action]),
        )

        assert await anext(generator) is session
        with pytest.raises(RuntimeError, match=error_message):
            await generator.asend(None)

        action.assert_not_awaited()
