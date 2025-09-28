from db.models import UserModel
from entrypoints.admin.views.base import ModelViewWithDeleteAction


class UserView(ModelViewWithDeleteAction, model=UserModel):
    icon = "fa-solid fa-user-tie"

    name = "Пользователь"
    name_plural = "Пользователи"

    can_create = True
    can_edit = False
    can_view_details = False
    can_delete = True
    can_export = False

    form_args = {}
    form_include_pk = True
    form_columns = [UserModel.username, UserModel.role]
    form_overrides = {}
    form_widget_args = {}
    form_ajax_refs = {}

    column_formatters = {
        UserModel.role: lambda user, _: user.role.label,  # type: ignore[attr-defined]
    }
    column_formatters_detail = {
        UserModel.role: lambda user, _: user.role.label,  # type: ignore[attr-defined]
    }
    column_labels = {
        UserModel.username: "Имя пользователя",
        UserModel.role: "Роль",
    }
    column_searchable_list = [UserModel.username]
    column_default_sort = (UserModel.username, True)
    column_sortable_list = [UserModel.username, UserModel.role]
    column_details_list = [UserModel.username, UserModel.role]
    column_list = [UserModel.username, UserModel.role]
