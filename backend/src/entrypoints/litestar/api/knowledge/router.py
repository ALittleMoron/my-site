from dishka.integrations.litestar import DishkaRouter

from entrypoints.litestar.api.knowledge.files.endpoints import (
    AdminKnowledgeFilesApiController,
)
from entrypoints.litestar.api.knowledge.items.endpoints import (
    AdminKnowledgeTagsApiController,
)
from entrypoints.litestar.api.knowledge.people.endpoints import AdminPeopleApiController

admin_router = DishkaRouter(
    "",
    route_handlers=[
        AdminPeopleApiController,
        AdminKnowledgeTagsApiController,
        AdminKnowledgeFilesApiController,
    ],
)
