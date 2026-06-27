from collections.abc import Mapping
from dataclasses import dataclass

from performance.query_plans.models import PlanExpectation, QueryThresholdGroup


@dataclass(frozen=True, slots=True)
class QueryThresholdPolicy:
    group_max_execution_ms: Mapping[QueryThresholdGroup, float]
    scenario_max_execution_ms: Mapping[str, float]
    query_max_execution_ms: Mapping[str, float]
    query_expected_index_names: Mapping[str, tuple[str, ...]]


def scenario_plan_expectation(  # noqa: PLR0913
    *,
    scenario_name: str,
    group: QueryThresholdGroup,
    policy: QueryThresholdPolicy,
    query_name: str | None,
    expected_index_names: tuple[str, ...],
    forbidden_seq_scan_relations: tuple[str, ...],
    allow_seq_scan_reason: str | None,
) -> PlanExpectation:
    effective_expected_index_names = (
        expected_index_names
        if query_name is None
        else policy.query_expected_index_names.get(query_name, expected_index_names)
    )
    if query_name is not None:
        query_override = policy.query_max_execution_ms.get(query_name)
        if query_override is not None:
            return PlanExpectation(
                max_execution_ms=query_override,
                threshold_source=f"override:{query_name}",
                expected_index_names=effective_expected_index_names,
                forbidden_seq_scan_relations=forbidden_seq_scan_relations,
                allow_seq_scan_reason=allow_seq_scan_reason,
            )
    scenario_override = policy.scenario_max_execution_ms.get(scenario_name)
    if scenario_override is not None:
        return PlanExpectation(
            max_execution_ms=scenario_override,
            threshold_source=f"override:{scenario_name}",
            expected_index_names=effective_expected_index_names,
            forbidden_seq_scan_relations=forbidden_seq_scan_relations,
            allow_seq_scan_reason=allow_seq_scan_reason,
        )
    return PlanExpectation(
        max_execution_ms=policy.group_max_execution_ms[group],
        threshold_source=f"group:{group.value}",
        expected_index_names=effective_expected_index_names,
        forbidden_seq_scan_relations=forbidden_seq_scan_relations,
        allow_seq_scan_reason=allow_seq_scan_reason,
    )


BALANCED_THRESHOLD_POLICY = QueryThresholdPolicy(
    group_max_execution_ms={
        QueryThresholdGroup.POINT_READ: 25.0,
        QueryThresholdGroup.LIST_READ: 250.0,
        QueryThresholdGroup.SEARCH: 150.0,
        QueryThresholdGroup.AGGREGATE: 250.0,
        QueryThresholdGroup.SMALL_WRITE: 100.0,
        QueryThresholdGroup.HEAVY: 300.0,
    },
    scenario_max_execution_ms={
        "articles_published_for_seo_sitemap": 250.0,
        "tags_short_en": 250.0,
        "resources_short_en": 250.0,
    },
    query_max_execution_ms={
        "articles_list_en_full_text_tag_date__002": 250.0,
        "articles_list_ru_full_text__002": 250.0,
    },
    query_expected_index_names={
        "managed_accounts_list__001": ("users_username_lower_uniq",),
        "managed_accounts_list__002": ("users_managed_accounts_list_idx",),
        "managed_accounts_update_role__001": ("users_username_lower_uniq",),
        "managed_accounts_update_role__002": ("users_username_idx",),
        "managed_accounts_update_password__001": ("users_username_lower_uniq",),
        "managed_accounts_update_password__002": ("users_username_idx",),
        "managed_accounts_activate__001": ("users_username_lower_uniq",),
        "managed_accounts_activate__002": ("users_username_idx",),
        "managed_accounts_deactivate__001": ("users_username_lower_uniq",),
        "managed_accounts_deactivate__002": ("users_username_idx",),
        "managed_accounts_delete__001": ("users_username_lower_uniq",),
        "managed_accounts_delete__002": ("users_username_idx",),
    },
)
