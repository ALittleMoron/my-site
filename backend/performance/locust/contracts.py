from pydantic import BaseModel, ValidationError


def validate_response_payload[ResponseSchemaT: BaseModel](
    *,
    payload: object,
    schema_type: type[ResponseSchemaT],
) -> ResponseSchemaT:
    try:
        return schema_type.model_validate(payload)
    except ValidationError as exc:
        msg = f"{schema_type.__name__} validation failed"
        raise ValueError(msg) from exc
