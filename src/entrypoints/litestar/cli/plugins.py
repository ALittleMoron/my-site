import click
from litestar import Litestar
from litestar.plugins import CLIPluginProtocol

from core.files.file_storages import FileStorage
from entrypoints.litestar.cli.commands.admin import create_admin_command
from entrypoints.litestar.cli.commands.files import collect_static
from entrypoints.litestar.cli.utils import run_sync
from ioc.container import container


class CLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: click.Group) -> None:
        @cli.command()
        @click.option("--username", "-U", help="Никнейм администратора")
        @click.option("--password", "-P", help="Пароль администратора")
        def createsuperuser(app: Litestar, username: str, password: str) -> None:  # noqa: ARG001
            """Создает нового администратора для админ-панели."""

            run_sync(create_admin_command(username, password))

        @cli.command()
        def initbuckets(app: Litestar) -> None:  # noqa: ARG001
            file_storage = run_sync(container.get(FileStorage))
            run_sync(file_storage.init_storage())

        @cli.command()
        def collectstatic(app: Litestar) -> None:  # noqa: ARG001
            """Синхронизирует static-файлы: закидывает их в minio."""

            file_storage = run_sync(container.get(FileStorage))
            run_sync(collect_static(file_storage=file_storage))
