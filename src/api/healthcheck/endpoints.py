from django.http import HttpRequest, HttpResponse
from ninja import Router
from verbose_http_exceptions import status

# TODO: Add advanced healthcheck (check db, cache, etc.)
router = Router()


@router.get(
    "base/",
    response=str,
    summary="Базовая проверка",
    description="Базовая проверка работоспособности приложения (Ответ 200 = живой)",
)
async def health(request: HttpRequest) -> HttpResponse:
    return HttpResponse(content="", status=status.HTTP_200_OK)
