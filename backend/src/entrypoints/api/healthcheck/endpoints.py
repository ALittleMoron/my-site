from fastapi import APIRouter, Response
from verbose_http_exceptions import status

api_router = APIRouter()


@api_router.get(
    "/healthcheck",
    summary="Базовая проверка",
    description="Базовая проверка работоспособности приложения (Ответ 200 = живой)",
)
async def health() -> Response:
    return Response(content="", status_code=status.HTTP_200_OK)
