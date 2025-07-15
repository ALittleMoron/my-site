import uuid
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Request, post
from litestar.middleware.rate_limit import DurationUnit, RateLimitConfig
from litestar.params import Body
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase
from entrypoints.views.contacts.schemas import ContactMeRequest

rate_limit: tuple[DurationUnit, int] = ("minute", 1)
rate_limit_config = RateLimitConfig(rate_limit=rate_limit)


@post(
    "",
    description="Создание заявки на то, чтобы связаться со мной",
    middleware=[rate_limit_config.middleware],
    name="contact-me-request",
)
async def contact_me_request(
    request: Request,
    contact_me_id: FromDishka[uuid.UUID],
    data: Annotated[ContactMeRequest, Body()],
    use_case: FromDishka[AbstractCreateContactMeRequestUseCase],
) -> Template:
    flag, message = data.is_valid()
    if flag is False:
        return HTMXTemplate()  # TODO: отправлять нотификацию о том, что данные невалидные
    await use_case.execute(
        form=data.to_schema(
            contact_me_id=contact_me_id,
            user_ip=request.client.host if request.client else "0.0.0.0",  # noqa: S104
        ),
    )
    return HTMXTemplate()  # TODO: отправить нотификацию о том, что запрос успешно прошёл


router = DishkaRouter("/contacts", route_handlers=[contact_me_request])
