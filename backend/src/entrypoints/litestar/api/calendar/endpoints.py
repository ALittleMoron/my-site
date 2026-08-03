from dishka import FromDishka
from dishka.integrations.litestar import DishkaRouter
from litestar import Controller, Request, get, status_codes
from litestar.datastructures import State

from core.auth.schemas import JwtUser
from core.auth.types import Token
from core.calendar.use_cases import CalendarUseCase
from entrypoints.litestar.api.calendar.schemas import CalendarResponseSchema
from entrypoints.litestar.api.parameters import CalendarReferenceDateQuery, CalendarWindowQuery
from entrypoints.litestar.guards import team_manager_guard
from infra.config.constants import constants


class AdminCalendarApiController(Controller):
    path = "/calendar"
    tags = ["admin calendar"]
    guards = [team_manager_guard]
    include_in_schema = False
    response_headers = {
        constants.knowledge_files.cache_control_header_name: (
            constants.knowledge_files.no_store_header_value
        ),
    }

    @get(
        "",
        description=(
            "Get the current author's memorable dates and birthdays for the selected calendar "
            "window."
        ),
        name="admin-calendar-api-handler",
        status_code=status_codes.HTTP_200_OK,
        cache=False,
    )
    async def get_calendar(
        self,
        reference_date: CalendarReferenceDateQuery,
        window: CalendarWindowQuery,
        request: Request[JwtUser, Token | None, State],
        use_case: FromDishka[CalendarUseCase],
    ) -> CalendarResponseSchema:
        return CalendarResponseSchema.from_domain_schema(
            schema=await use_case.get_calendar(
                reference_date=reference_date,
                window=window,
                author_username=request.user.username,
            ),
        )


admin_router = DishkaRouter("", route_handlers=[AdminCalendarApiController])
