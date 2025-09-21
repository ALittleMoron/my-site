from dishka.integrations.litestar import DishkaRouter
from litestar import Response, get
from verbose_http_exceptions import status

from config.settings import settings


@get(
    "",
    summary="Базовая проверка",
    description="Базовая проверка работоспособности приложения (Ответ 200 = живой)",
    cache=settings.app.get_cache_duration(1),  # 1 секунда
)
async def health() -> Response:
    return Response(content="", status_code=status.HTTP_200_OK)


api_router = DishkaRouter("/healthcheck", route_handlers=[health])
