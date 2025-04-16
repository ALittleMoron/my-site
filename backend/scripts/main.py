from typing import Annotated

import typer

from async_typer import AsyncTyper
from config.initializers import check_certs_exists

cli = AsyncTyper()


@cli.async_command()
async def createsuperuser(
    username: Annotated[str, typer.Option(help="Никнейм администратора")],
    password: Annotated[str, typer.Option(help="Пароль администратора")],
):
    """Создает нового администратора для админ-панели."""
    from commands.admin import create_admin_command

    await create_admin_command(username, password)


if __name__ == "__main__":
    check_certs_exists()
    cli()
