import uuid
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, post
from litestar.params import Body
from verbose_http_exceptions import status

from core.contacts.use_cases import AbstractContactsUseCase
from entrypoints.litestar.api.contacts.schemas import ContactMeRequest


class ContactsApiController(Controller):
    path = "/contacts"
    tags = ["contacts"]

    @post(
        "",
        status_code=status.HTTP_204_NO_CONTENT,
        description="Создание заявки на то, чтобы связаться со мной",
    )
    async def contact_me_request(
        self,
        contact_me_id: FromDishka[uuid.UUID],
        data: Annotated[ContactMeRequest, Body()],
        use_case: FromDishka[AbstractContactsUseCase],
    ) -> None:
        await use_case.create_contact_me_request(form=data.to_schema(contact_me_id=contact_me_id))


api_router = DishkaRouter("", route_handlers=[ContactsApiController])
