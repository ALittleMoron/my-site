from datetime import UTC, datetime
from typing import Any

from sqladmin import ModelView, action
from sqladmin.helpers import get_object_identifier
from starlette.datastructures import URL, FormData
from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.enums import PublishStatusEnum


class AdminModelView(ModelView):

    @staticmethod
    def get_pks(request: Request) -> list[str]:
        return request.query_params.get("pks", "").split(",")

    def make_redirect_response(self, request: Request) -> RedirectResponse:
        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    def get_save_redirect_url(
        self,
        request: Request,
        form: FormData,
        model_view: ModelView,
        obj: Any,
    ) -> str | URL:
        identity = request.path_params["identity"]
        identifier = get_object_identifier(obj)
        if form.get("save") == "Сохранить":
            return request.url_for("admin:list", identity=identity)
        elif form.get("save") == "Сохранить и продолжить редактировать" or (
            form.get("save") == "Сохранить как новое" and model_view.save_as_continue
        ):
            return request.url_for("admin:edit", identity=identity, pk=identifier)
        return request.url_for("admin:create", identity=identity)


class ModelViewWithDeleteAction(AdminModelView):
    @action(
        name="delete_entities",
        label="Удалить",
        confirmation_message="Вы уверены?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def delete_entities(self, request: Request) -> RedirectResponse:
        pks = self.get_pks(request)
        for pk in pks or []:
            await self.delete_model(request, pk)
        return self.make_redirect_response(request=request)


class ModelViewWithPublishAction(AdminModelView):
    @action(
        name="publish_entities",
        label="Опубликовать",
        confirmation_message="Вы уверены?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def publish_entities(self, request: Request) -> RedirectResponse:
        pks = self.get_pks(request)
        data = {"published_at": datetime.now(tz=UTC), "publish_status": PublishStatusEnum.PUBLISHED}
        for pk in pks or []:
            await self.update_model(request, pk, data)
        return self.make_redirect_response(request=request)

    @action(
        name="draft_entities",
        label="Снять с публикации",
        confirmation_message="Вы уверены?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def draft_entities(self, request: Request) -> RedirectResponse:
        pks = self.get_pks(request)
        data = {"published_at": None, "publish_status": PublishStatusEnum.DRAFT}
        for pk in pks or []:
            await self.update_model(request, pk, data)
        return self.make_redirect_response(request=request)
