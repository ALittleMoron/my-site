from dataclasses import dataclass

from core.schemas import ValuedDataclass
from core.wiki_links.enums import WikiLinkTargetTypeEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class WikiLinkTargetGroup:
    type: WikiLinkTargetTypeEnum
    slugs: list[str]


@dataclass(frozen=True, slots=True, kw_only=True)
class WikiLinkTargets(ValuedDataclass[WikiLinkTargetGroup]): ...
