from types import TracebackType
from typing import Protocol, Self

from pydantic import BaseModel

from performance.contracts import validate_response_payload

HTTP_OK = 200


class LocustResponse(Protocol):
    status_code: int

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def json(self) -> object: ...

    def failure(self, message: str) -> None: ...


class LocustHttpClient(Protocol):
    def get(self, path: str, **kwargs: object) -> LocustResponse: ...


class PerformanceApiClient:
    def __init__(self, *, client: LocustHttpClient, validate_responses: bool) -> None:
        self.client = client
        self.validate_responses = validate_responses

    def get[ResponseSchemaT: BaseModel](
        self,
        path: str,
        *,
        name: str,
        schema_type: type[ResponseSchemaT],
    ) -> ResponseSchemaT | None:
        if self.validate_responses:
            return self.get_validated(path, name=name, schema_type=schema_type)
        self.client.get(path, name=name)
        return None

    def get_validated[ResponseSchemaT: BaseModel](
        self,
        path: str,
        *,
        name: str,
        schema_type: type[ResponseSchemaT],
    ) -> ResponseSchemaT | None:
        with self.client.get(path, name=name, catch_response=True) as response:
            if response.status_code != HTTP_OK:
                response.failure(f"{name} returned {response.status_code}")
                return None
            try:
                return validate_response_payload(
                    payload=response.json(),
                    schema_type=schema_type,
                )
            except ValueError as exc:
                response.failure(str(exc))
                return None
