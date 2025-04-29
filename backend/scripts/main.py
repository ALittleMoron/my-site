from typing import Annotated

import typer
from miniopy_async import Minio

from async_typer import AsyncTyper
from config.initializers import check_certs_exists
from config.settings import settings
from ioc.container import container

cli = AsyncTyper()


@cli.async_command()
async def createsuperuser(
    username: Annotated[str, typer.Option(help="Никнейм администратора")],
    password: Annotated[str, typer.Option(help="Пароль администратора")],
):
    """Создает нового администратора для админ-панели."""
    from commands.admin import create_admin_command

    await create_admin_command(username, password)


@cli.async_command()
async def collectstatic() -> None:
    """Синхронизирует static-файлы: закидывает их в minio."""
    from commands.files import collect_static

    await collect_static(
        static_files_path=settings.dir.src_path / 'static',
        client=await container.get(Minio),
    )


if __name__ == "__main__":
    check_certs_exists()
    cli()
