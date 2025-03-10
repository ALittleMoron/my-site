from typing import Literal

from litestar import MediaType, Router, get, status_codes


@get(
    "base/",
    media_type=MediaType.TEXT,
    status_code=status_codes.HTTP_200_OK,
    description="Базовая проверка работоспособности приложения (Ответ 200 = живой)",
)
async def health() -> Literal[""]:
    return ""


# TODO: Add advanced healthcheck (check db, cache, etc.)
router = Router(
    "/health/",
    route_handlers=[health],
    tags=["healthcheck"],
)
