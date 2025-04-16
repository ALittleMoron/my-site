from sqlalchemy.ext.asyncio import AsyncSession
from typer import secho

from core.auth.schemas import RoleEnum
from core.auth.utils import Hasher
from db.models.auth import UserModel
from ioc.container import container


async def create_admin_command(username: str, password: str):
    async with container() as request_container:
        hasher = await request_container.get(Hasher)
        session = await request_container.get(AsyncSession)
        hashed_password = hasher.hash_password(password)
        try:
            admin = UserModel(
                username=username,
                password=hashed_password,
                role=RoleEnum.ADMIN,
            )
            session.add(admin)
            await session.commit()
        except Exception as exc:
            secho(f"Внутренняя ошибка: {exc}", fg="red")
        else:
            secho("Администратор успешно создан.", fg="green")
