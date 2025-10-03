from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from core.files.schemas import PresignPutObjectParams
from core.files.use_cases import AbstractPresignPutObjectUseCase
from ioc.container import container


async def presign_put_media_file(request: Request) -> Response:
    if "content_type" not in request.query_params:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content type is required",
        )
    async with container() as request_container:
        use_case = await request_container.get(AbstractPresignPutObjectUseCase)
        urls = await use_case.execute(
            params=PresignPutObjectParams(
                content_type=request.query_params["content_type"],
                folder="admin",
                namespace="media",
            ),
        )
    return JSONResponse({"uploadUrl": urls.upload_url, "accessUrl": urls.access_url})
