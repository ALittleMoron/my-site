from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action


class ModelViewWithAction(ModelView):
    @action(
        name="delete_entities",
        label="Удалить выбранные сущности",
        confirmation_message="Вы уверены?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def delete_entities(self, request: Request) -> RedirectResponse:
        pks = request.query_params.get("pks", "").split(",")
        for pk in pks or []:
            await self.delete_model(request, pk)

        referer = request.headers.get("Referer")
        if referer:
            return RedirectResponse(referer)
        else:
            return RedirectResponse(request.url_for("admin:list", identity=self.identity))
