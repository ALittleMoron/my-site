from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.loggers import logger
from core.users.enums import RoleEnum
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
            msg = "Ошибка базы данных"
            logger.error(msg)
            await session.rollback()
        except Exception as exc:  # noqa: BLE001
            msg = f"Внутренняя ошибка: {exc!s}"
            logger.error(msg)
        else:
            msg = "Администратор успешно создан."
            logger.info(msg)
