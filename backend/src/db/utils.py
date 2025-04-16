from alembic.command import downgrade as alembic_downgrade
from alembic.command import upgrade as alembic_upgrade
from alembic.config import Config

from config.settings import settings


def migrate(revision: str) -> None:
    config = Config(settings.dir.src_path / "db" / "alembic" / "alembic.ini")
    alembic_upgrade(config=config, revision=revision)


def downgrade(revision: str) -> None:
    config = Config(settings.dir.src_path / "db" / "alembic" / "alembic.ini")
    alembic_downgrade(config=config, revision=revision)
