import click
from litestar import Litestar
from litestar.plugins import CLIPluginProtocol
from miniopy_async.api import Minio

from config.constants import constants
from entrypoints.litestar.cli.commands.admin import create_admin_command
from entrypoints.litestar.cli.commands.files import collect_static, init_buckets
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
            client = run_sync(container.get(Minio))
            run_sync(init_buckets(client=client))

        @cli.command()
        def collectstatic(app: Litestar) -> None:  # noqa: ARG001
            """Синхронизирует static-файлы: закидывает их в minio."""

            client = run_sync(container.get(Minio))
            run_sync(
                collect_static(
                    static_files_path=constants.dir.src_path / "static",
                    client=client,
                ),
            )
