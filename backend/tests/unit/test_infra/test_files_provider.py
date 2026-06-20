from types import TracebackType
from unittest.mock import AsyncMock, Mock, patch

from dishka import make_async_container
from miniopy_async.api import Minio

from infra.ioc.prodivers.files_provider import FilesProvider


class MinioContextManagerDouble:
    def __init__(self) -> None:
        self.client = Mock(spec=Minio)
        self.close_session = AsyncMock()
        self.entered = False
        self.exited = False
        self.exit_args: (
            tuple[type[BaseException] | None, BaseException | None, TracebackType | None] | None
        ) = None

    async def __aenter__(self) -> Minio:
        self.entered = True
        return self.client

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True
        self.exit_args = (exc_type, exc_value, traceback)


class TestFilesProvider:
    async def test_minio_client_exits_context_when_container_closes(self) -> None:
        minio_context_manager = MinioContextManagerDouble()

        with patch("infra.ioc.prodivers.files_provider.Minio", return_value=minio_context_manager):
            container = make_async_container(FilesProvider())
            try:
                provided_client = await container.get(Minio)
            finally:
                await container.close()

        assert provided_client is minio_context_manager.client
        assert minio_context_manager.entered is True
        assert minio_context_manager.exited is True
        assert minio_context_manager.exit_args == (None, None, None)
        minio_context_manager.close_session.assert_not_awaited()
