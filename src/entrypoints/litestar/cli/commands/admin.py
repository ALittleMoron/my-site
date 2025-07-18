from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typer import secho

from core.users.schemas import RoleEnum
from db.models.auth import UserModel
from entrypoints.admin.auth.utils import Hasher
from ioc.container import container


async def create_admin_command(username: str, password: str) -> None:
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
        except SQLAlchemyError:
            secho("Ошибка базы данных", fg="red")
            await session.rollback()
        except Exception as exc:  # noqa: BLE001
            secho(f"Внутренняя ошибка: {exc!s}", fg="red")
        else:
            secho("Администратор успешно создан.", fg="green")
