from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import (
    JsonRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    StoplightRenderPlugin,
    SwaggerRenderPlugin,
    YamlRenderPlugin,
)
from litestar.openapi.spec import Contact, License, Server, Tag

from app.utils import get_app_version

description = """
Документация API моего личного сайта.

Данное API можно использовать извне, если вам это будет нужно. Тут пока нет никаких аккаунтов и
данные хранятся только мои. Если вам интересно, можете использовать.
"""

openapi_config = OpenAPIConfig(
    title="API личного сайта",
    version=get_app_version(),
    create_examples=True,
    random_seed=1,
    contact=Contact(
        name="Дмитрий Лунев",
        email="dima.lunev14@gmail.com",
    ),
    description=description,
    external_docs=None,
    license=License(
        name="MIT License",
        identifier="MIT ",
        url="https://opensource.org/license/mit/",
    ),
    security=None,
    servers=[Server('/', description="Локальный сервер, запущенный на вашей машине.")],
    summary=None,
    tags=[
        Tag(name="health-check", description="Проверка работоспособности приложения"),
    ],
    terms_of_service=None,
    use_handler_docstrings=True,
    render_plugins=[
        StoplightRenderPlugin(),
        JsonRenderPlugin(),
        YamlRenderPlugin(),
        RapidocRenderPlugin(),
        RedocRenderPlugin(),
        SwaggerRenderPlugin(),
    ],
    path="/docs",
    root_schema_site="swagger",
    enabled_endpoints=None,
)
