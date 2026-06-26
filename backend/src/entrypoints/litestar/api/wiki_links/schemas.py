from typing import Annotated, Self

from pydantic import Field

from core.wiki_links.enums import WikiLinkTargetTypeEnum
from core.wiki_links.schemas import WikiLinkTargetGroup, WikiLinkTargets
from entrypoints.litestar.api.schemas import CamelCaseSchema


class WikiLinkTargetGroupResponseSchema(CamelCaseSchema):
    type: Annotated[WikiLinkTargetTypeEnum, Field(title="Target type")]
    slugs: Annotated[list[str], Field(title="Target slugs")]

    @classmethod
    def from_domain_schema(cls, *, schema: WikiLinkTargetGroup) -> Self:
        return cls(type=schema.type, slugs=schema.slugs)


class WikiLinkTargetsResponseSchema(CamelCaseSchema):
    targets: Annotated[list[WikiLinkTargetGroupResponseSchema], Field(title="Targets")]

    @classmethod
    def from_domain_schema(cls, *, schema: WikiLinkTargets) -> Self:
        return cls(
            targets=[
                WikiLinkTargetGroupResponseSchema.from_domain_schema(schema=target)
                for target in schema
            ],
        )
