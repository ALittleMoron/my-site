import uuid
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Request, post
from litestar.middleware.rate_limit import DurationUnit, RateLimitConfig
from litestar.params import Body
from verbose_http_exceptions import status

from config.settings import settings
from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase
from entrypoints.api.contacts.schemas import ContactMeRequest

rate_limit: tuple[DurationUnit, int] = ("minute", 1)
rate_limit_config = RateLimitConfig(rate_limit=rate_limit)


@post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Создание заявки на то, чтобы связаться со мной",
    middleware=[rate_limit_config.middleware] if settings.app.use_rate_limit else [],
)
async def contact_me_request(
    request: Request,
    contact_me_id: FromDishka[uuid.UUID],
    data: Annotated[ContactMeRequest, Body()],
    use_case: FromDishka[AbstractCreateContactMeRequestUseCase],
) -> None:
    await use_case.execute(
        form=data.to_schema(
            contact_me_id=contact_me_id,
            user_ip=request.client.host if request.client else "<no ip found>",
        ),
    )


api_router = DishkaRouter("/contacts", route_handlers=[contact_me_request])
