from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from performance.query_plans.models import ExpectedIndex, PlanExpectation, QueryThresholdGroup


@dataclass(frozen=True, slots=True)
class QueryThresholdPolicy:
    group_max_execution_ms: Mapping[QueryThresholdGroup, float]
    scenario_max_execution_ms: Mapping[str, float]
    query_max_execution_ms: Mapping[str, float]
    query_expected_indexes: Mapping[str, tuple[ExpectedIndex, ...]]


def scenario_plan_expectation(  # noqa: PLR0913
    *,
    scenario_name: str,
    group: QueryThresholdGroup,
    policy: QueryThresholdPolicy,
    query_name: str | None,
    expected_indexes: tuple[ExpectedIndex, ...],
    forbidden_seq_scan_relations: tuple[str, ...],
    allow_seq_scan_reason: str | None,
) -> PlanExpectation:
    effective_expected_indexes = (
        expected_indexes
        if query_name is None
        else policy.query_expected_indexes.get(query_name, expected_indexes)
    )
    if query_name is not None:
        query_override = policy.query_max_execution_ms.get(query_name)
        if query_override is not None:
            return PlanExpectation(
                max_execution_ms=query_override,
                threshold_source=f"override:{query_name}",
                expected_indexes=effective_expected_indexes,
                forbidden_seq_scan_relations=forbidden_seq_scan_relations,
                allow_seq_scan_reason=allow_seq_scan_reason,
            )
    scenario_override = policy.scenario_max_execution_ms.get(scenario_name)
    if scenario_override is not None:
        return PlanExpectation(
            max_execution_ms=scenario_override,
            threshold_source=f"override:{scenario_name}",
            expected_indexes=effective_expected_indexes,
            forbidden_seq_scan_relations=forbidden_seq_scan_relations,
            allow_seq_scan_reason=allow_seq_scan_reason,
        )
    return PlanExpectation(
        max_execution_ms=policy.group_max_execution_ms[group],
        threshold_source=f"group:{group.value}",
        expected_indexes=effective_expected_indexes,
        forbidden_seq_scan_relations=forbidden_seq_scan_relations,
        allow_seq_scan_reason=allow_seq_scan_reason,
    )


INDEX_RELATION_NAMES: Mapping[str, str] = {
    "articles__article_folder_model_pkey": "articles__article_folder_model",
    "articles__tag_model_pkey": "articles__tag_model",
    "articles_article_publish_status_published_updated_idx": "articles__article_model",
    "articles_article_tree_folder_en_published_idx": "articles__article_model",
    "articles_folder_key_lower_uniq": "articles__article_folder_model",
    "articles_tag_name_en_trgm_idx": "articles__tag_model",
    "articles_tag_name_ru_trgm_idx": "articles__tag_model",
    "articles_tag_slug_trgm_idx": "articles__tag_model",
    "auth__auth_session_model_pkey": "auth__auth_session_model",
    "auth_sessions_expiry_idx": "auth__auth_session_model",
    "auth_sessions_secret_hash_uniq": "auth__auth_session_model",
    "auth_sessions_username_lower_active_expiry_idx": "auth__auth_session_model",
    "auth_sessions_username_lower_active_last_used_idx": "auth__auth_session_model",
    "cm_external_resource_name_en_trgm_idx": "competency_matrix__external_resource_model",
    "cm_external_resource_name_ru_trgm_idx": "competency_matrix__external_resource_model",
    "cm_external_resource_url_trgm_idx": "competency_matrix__external_resource_model",
    "cm_queued_question_fifo_idx": "competency_matrix__queued_question_model",
    "cm_queued_question_fingerprint_idx": "competency_matrix__queued_question_model",
    "cmi_question_en_fingerprint_idx": "competency_matrix__competency_matrix_item_model",
    "cmi_question_ru_fingerprint_idx": "competency_matrix__competency_matrix_item_model",
    "competency_matrix__competency_matrix_subsection_model_pkey": (
        "competency_matrix__competency_matrix_subsection_model"
    ),
    "competency_matrix__external_resource_model_pkey": (
        "competency_matrix__external_resource_model"
    ),
    "competency_matrix__queued_question_model_pkey": ("competency_matrix__queued_question_model"),
    "knowledge__knowledge_file_model_pkey": "knowledge__knowledge_file_model",
    "knowledge__date_details_model_pkey": "knowledge__date_details_model",
    "knowledge__date_person_model_pkey": "knowledge__date_person_model",
    "knowledge__knowledge_item_model_pkey": "knowledge__knowledge_item_model",
    "knowledge__knowledge_item_tag_model_pkey": "knowledge__knowledge_item_tag_model",
    "knowledge__knowledge_tag_model_pkey": "knowledge__knowledge_tag_model",
    "knowledge__person_details_model_pkey": "knowledge__person_details_model",
    "knowledge__person_relationship_model_pkey": "knowledge__person_relationship_model",
    "knowledge__person_relationship_type_model_pkey": ("knowledge__person_relationship_type_model"),
    "knowledge_files_author_item_kind_id_idx": "knowledge__knowledge_file_model",
    "knowledge_files_id_author_uniq": "knowledge__knowledge_file_model",
    "date_details_author_calendar_item_idx": "knowledge__date_details_model",
    "date_details_id_author_uniq": "knowledge__date_details_model",
    "date_people_author_date_person_idx": "knowledge__date_person_model",
    "date_people_author_person_date_idx": "knowledge__date_person_model",
    "knowledge_item_tags_author_tag_item_idx": "knowledge__knowledge_item_tag_model",
    "knowledge_items_author_kind_name_id_idx": "knowledge__knowledge_item_model",
    "knowledge_items_author_kind_updated_id_idx": "knowledge__knowledge_item_model",
    "knowledge_items_id_author_uniq": "knowledge__knowledge_item_model",
    "knowledge_items_display_name_trgm_idx": "knowledge__knowledge_item_model",
    "knowledge_tags_id_author_uniq": "knowledge__knowledge_tag_model",
    "knowledge_tags_author_name_id_idx": "knowledge__knowledge_tag_model",
    "knowledge_tags_author_name_lower_uniq": "knowledge__knowledge_tag_model",
    "knowledge_tags_name_trgm_idx": "knowledge__knowledge_tag_model",
    "person_details_email_trgm_idx": "knowledge__person_details_model",
    "person_details_first_name_trgm_idx": "knowledge__person_details_model",
    "person_details_last_name_trgm_idx": "knowledge__person_details_model",
    "person_details_middle_name_trgm_idx": "knowledge__person_details_model",
    "person_details_author_birthday_item_idx": "knowledge__person_details_model",
    "person_details_id_author_uniq": "knowledge__person_details_model",
    "person_relationship_types_id_author_uniq": ("knowledge__person_relationship_type_model"),
    "person_relationship_types_author_name_id_idx": ("knowledge__person_relationship_type_model"),
    "person_relationships_author_source_idx": "knowledge__person_relationship_model",
    "person_relationships_author_target_idx": "knowledge__person_relationship_model",
    "person_relationships_author_type_id_idx": "knowledge__person_relationship_model",
    "resumes__resume_model_pkey": "resumes__resume_model",
    "resumes_resume_author_updated_id_idx": "resumes__resume_model",
    "users_managed_accounts_list_idx": "auth__user_model",
    "users_username_idx": "auth__user_model",
    "users_username_lower_uniq": "auth__user_model",
}


def expected_indexes_from_names(*, names: Iterable[str]) -> tuple[ExpectedIndex, ...]:
    try:
        return tuple(
            ExpectedIndex(name=name, relation_name=INDEX_RELATION_NAMES[name]) for name in names
        )
    except KeyError as error:
        msg = f"Query-plan index {error.args[0]!r} has no owning relation mapping"
        raise ValueError(msg) from error


ABSOLUTE_SLA_POLICY = QueryThresholdPolicy(
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
        "resources_short_en": 300.0,
    },
    query_max_execution_ms={
        "articles_list_en_full_text_tag_date__002": 250.0,
        "articles_list_ru_full_text__002": 250.0,
    },
    query_expected_indexes={
        "managed_accounts_list__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_list__002": expected_indexes_from_names(
            names=("users_managed_accounts_list_idx",),
        ),
        "managed_accounts_update_role__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_update_role__002": expected_indexes_from_names(
            names=("users_username_idx",),
        ),
        "managed_accounts_update_password__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_update_password__002": expected_indexes_from_names(
            names=("users_username_idx",),
        ),
        "managed_accounts_activate__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_activate__002": expected_indexes_from_names(
            names=("users_username_idx",),
        ),
        "managed_accounts_deactivate__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_deactivate__002": expected_indexes_from_names(
            names=("users_username_idx",),
        ),
        "managed_accounts_delete__001": expected_indexes_from_names(
            names=("users_username_lower_uniq",),
        ),
        "managed_accounts_delete__002": expected_indexes_from_names(
            names=("users_username_idx",),
        ),
        "resumes_list_workspace__001": expected_indexes_from_names(
            names=("resumes_resume_author_updated_id_idx",),
        ),
        "resumes_list_workspace__002": (),
        "knowledge_item_detail__001": expected_indexes_from_names(
            names=("knowledge_items_id_author_uniq",),
        ),
        "knowledge_item_detail__002": expected_indexes_from_names(
            names=("knowledge__knowledge_item_tag_model_pkey",),
        ),
        "knowledge_item_for_author__001": expected_indexes_from_names(
            names=("knowledge_items_id_author_uniq",),
        ),
        "knowledge_item_for_author__002": expected_indexes_from_names(
            names=("knowledge__knowledge_item_tag_model_pkey",),
        ),
        "knowledge_items_by_ids__001": expected_indexes_from_names(
            names=("knowledge__knowledge_item_model_pkey",),
        ),
        "knowledge_items_by_ids__002": expected_indexes_from_names(
            names=("knowledge__knowledge_item_tag_model_pkey",),
        ),
        "people_page_search_and_tags__001": expected_indexes_from_names(
            names=(
                "knowledge_item_tags_author_tag_item_idx",
                "knowledge_items_id_author_uniq",
                "knowledge__person_details_model_pkey",
            ),
        ),
        "people_page_search_and_tags__002": expected_indexes_from_names(
            names=(
                "knowledge_item_tags_author_tag_item_idx",
                "knowledge_items_id_author_uniq",
                "knowledge__person_details_model_pkey",
            ),
        ),
        "knowledge_dates_page_calendar__001": expected_indexes_from_names(
            names=(
                "date_details_author_calendar_item_idx",
                "knowledge__knowledge_item_model_pkey",
            ),
        ),
        "knowledge_dates_page_search__001": expected_indexes_from_names(
            names=(
                "knowledge_items_author_kind_name_id_idx",
                "date_details_id_author_uniq",
            ),
        ),
        "knowledge_dates_page_search__002": expected_indexes_from_names(
            names=("knowledge_items_display_name_trgm_idx",),
        ),
        "knowledge_dates_page_search_tags_person__001": expected_indexes_from_names(
            names=(
                "knowledge_item_tags_author_tag_item_idx",
                "date_people_author_person_date_idx",
                "date_details_id_author_uniq",
                "knowledge__knowledge_item_model_pkey",
            ),
        ),
        "knowledge_dates_page_search_tags_person__002": expected_indexes_from_names(
            names=(
                "knowledge_item_tags_author_tag_item_idx",
                "date_people_author_person_date_idx",
                "date_details_id_author_uniq",
                "knowledge__knowledge_item_model_pkey",
            ),
        ),
    },
)
