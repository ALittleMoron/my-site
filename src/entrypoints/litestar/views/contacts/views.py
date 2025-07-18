import uuid
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Request, post
from litestar.middleware.rate_limit import DurationUnit, RateLimitConfig
from litestar.params import Body
from litestar.plugins.htmx import HTMXTemplate
from litestar.response import Template

from config.settings import settings
from core.contacts.use_cases import AbstractCreateContactMeRequestUseCase
from entrypoints.litestar.views.contacts.context_converters import ContactsContextConverter
from entrypoints.litestar.views.contacts.schemas import ContactMeRequest

rate_limit: tuple[DurationUnit, int] = ("minute", 1)
rate_limit_config = RateLimitConfig(rate_limit=rate_limit)


@post(
    "",
    description="Создание заявки на то, чтобы связаться со мной",
    middleware=[rate_limit_config.middleware] if settings.app.use_rate_limit else [],
    name="contact-me-request",
)
async def contact_me_request(
    request: Request,
    contact_me_id: FromDishka[uuid.UUID],
    data: Annotated[ContactMeRequest, Body()],
    context_converter: FromDishka[ContactsContextConverter],
    use_case: FromDishka[AbstractCreateContactMeRequestUseCase],
) -> Template:
    await use_case.execute(
        form=data.to_schema(
            contact_me_id=contact_me_id,
            user_ip=request.client.host if request.client else "0.0.0.0",  # noqa: S104
        ),
    )
    return HTMXTemplate(
        re_swap="afterbegin",
        re_target="#alerts",
        template_name="base/blocks/alert.html",
        context=context_converter.alert_context(
            alert_type="success",
            message="Запрос успешно отправлен",
        ),
    )


router = DishkaRouter("/contacts", route_handlers=[contact_me_request])
