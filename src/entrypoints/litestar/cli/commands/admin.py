from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.loggers import logger
from core.auth.enums import RoleEnum
from core.auth.password_hashers import PasswordHasher
from db.models.auth import UserModel
from ioc.container import container


async def create_admin_command(username: str, password: str) -> None:
    async with container() as request_container:
        hasher = await request_container.get(PasswordHasher)
        session = await request_container.get(AsyncSession)
        hashed_password = hasher.hash_password(password)
        try:
            admin = UserModel(
                username=username,
                password_hash=hashed_password,
                role=RoleEnum.ADMIN,
            )
            session.add(admin)
            await session.commit()
        except SQLAlchemyError:
            msg = "Ошибка базы данных"
            logger.exception(msg)
            await session.rollback()
        except Exception as exc:  # noqa: BLE001
            msg = f"Внутренняя ошибка: {exc!s}"
            logger.exception(msg)
        else:
            msg = "Администратор успешно создан."
            logger.info(msg)
