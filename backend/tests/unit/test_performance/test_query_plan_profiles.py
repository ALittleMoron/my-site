import pytest

from performance.query_plans import models as query_plan_models
from performance.query_plans.expectations import ABSOLUTE_SLA_POLICY
from performance.query_plans.runner import get_profile
from performance.query_plans.scenarios import STORAGE_SCENARIOS


class TestQueryPlanProfiles:
    def test_realistic_profile_has_explicit_representative_cardinalities(self) -> None:
        profile = get_profile(name="realistic")

        assert profile is query_plan_models.REALISTIC_PROFILE
        assert profile.name == "realistic"
        assert profile.timing_mode is query_plan_models.TimingMode.ENFORCE
        assert profile.explain_runs == 3
        assert profile.explain_work_mem_mb == 16
        assert profile.cardinalities == query_plan_models.ProfileCardinalities(
            auth=query_plan_models.AuthCardinalities(users=100, sessions=500),
            articles=query_plan_models.ArticleCardinalities(
                folders=20,
                articles=5_000,
                published_percentage=80,
                fts_match_percentage=1,
                tags=500,
                article_tag_links=20_000,
                daily_analytics=100_000,
                reactions=10_000,
            ),
            resumes=query_plan_models.ResumeCardinalities(resumes=250),
            knowledge=query_plan_models.KnowledgeCardinalities(
                items=5_000,
                dates=5_000,
                search_match_percentage=10,
                tags=500,
                item_tag_links=20_000,
                date_tag_links=20_000,
                relationship_types=100,
                relationships=20_000,
                date_person_links=20_000,
                files=10_000,
            ),
            matrix=query_plan_models.MatrixCardinalities(
                sheets=20,
                sections_per_sheet=8,
                subsections_per_section=12,
                items=10_000,
                resources=5_000,
                resource_links=25_000,
                queued_questions=5_000,
            ),
            agent_access=query_plan_models.AgentAccessCardinalities(audit_events=10_000),
        )

    def test_stress_profile_has_explicit_large_cardinalities(self) -> None:
        profile = get_profile(name="stress")

        assert profile is query_plan_models.STRESS_PROFILE
        assert profile.name == "stress"
        assert profile.timing_mode is query_plan_models.TimingMode.OBSERVE
        assert profile.explain_runs == 3
        assert profile.explain_work_mem_mb == 64
        assert profile.cardinalities == query_plan_models.ProfileCardinalities(
            auth=query_plan_models.AuthCardinalities(users=10_000, sessions=50_000),
            articles=query_plan_models.ArticleCardinalities(
                folders=200,
                articles=200_000,
                published_percentage=80,
                fts_match_percentage=1,
                tags=30_000,
                article_tag_links=500_000,
                daily_analytics=2_000_000,
                reactions=500_000,
            ),
            resumes=query_plan_models.ResumeCardinalities(resumes=50_000),
            knowledge=query_plan_models.KnowledgeCardinalities(
                items=200_000,
                dates=200_000,
                search_match_percentage=10,
                tags=30_000,
                item_tag_links=500_000,
                date_tag_links=500_000,
                relationship_types=10_000,
                relationships=500_000,
                date_person_links=500_000,
                files=500_000,
            ),
            matrix=query_plan_models.MatrixCardinalities(
                sheets=20,
                sections_per_sheet=8,
                subsections_per_section=12,
                items=200_000,
                resources=200_000,
                resource_links=500_000,
                queued_questions=50_000,
            ),
            agent_access=query_plan_models.AgentAccessCardinalities(audit_events=250_000),
        )

    def test_profiles_expose_relation_cardinalities_for_plan_classification(self) -> None:
        profile = query_plan_models.REALISTIC_PROFILE

        assert profile.relation_cardinalities == {
            "auth__user_model": 100,
            "auth__auth_session_model": 500,
            "articles__article_folder_model": 20,
            "articles__article_model": 5_000,
            "articles__tag_model": 500,
            "articles__article_to_tag_secondary_model": 20_000,
            "articles__article_daily_analytics_model": 100_000,
            "articles__article_reaction_model": 10_000,
            "resumes__resume_model": 250,
            "knowledge__knowledge_item_model": 10_000,
            "knowledge__knowledge_tag_model": 500,
            "knowledge__knowledge_item_tag_model": 40_000,
            "knowledge__person_details_model": 5_000,
            "knowledge__date_details_model": 5_000,
            "knowledge__date_person_model": 20_000,
            "knowledge__person_relationship_type_model": 100,
            "knowledge__person_relationship_model": 20_000,
            "knowledge__knowledge_file_model": 10_000,
            "competency_matrix__competency_matrix_sheet_model": 20,
            "competency_matrix__competency_matrix_section_model": 160,
            "competency_matrix__competency_matrix_subsection_model": 1_920,
            "competency_matrix__competency_matrix_item_model": 10_000,
            "competency_matrix__external_resource_model": 5_000,
            "competency_matrix__resource_to_item_secondary_model": 25_000,
            "competency_matrix__queued_question_model": 5_000,
            "agent_access__agent_audit_event_model": 10_000,
        }

    def test_balanced_profile_is_not_supported(self) -> None:
        assert not hasattr(query_plan_models, "BALANCED_PROFILE")
        assert not hasattr(query_plan_models, "DatasetProfile")

        with pytest.raises(ValueError, match="Unknown query plan profile: balanced"):
            get_profile(name="balanced")

    def test_resource_search_plan_shape_requires_trigram_indexes_for_scaled_profiles(
        self,
    ) -> None:
        scenario = next(
            scenario for scenario in STORAGE_SCENARIOS if scenario.name == "resources_exact_en"
        )

        realistic_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.REALISTIC_PROFILE,
        )
        stress_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        expected_indexes = {
            "cm_external_resource_name_en_trgm_idx",
            "cm_external_resource_name_ru_trgm_idx",
            "cm_external_resource_url_trgm_idx",
        }
        for expectation in (realistic_expectation, stress_expectation):
            assert {index.name for index in expectation.expected_indexes} == expected_indexes
            assert expectation.forbidden_seq_scan_relations == (
                "competency_matrix__external_resource_model",
            )
            assert expectation.allow_seq_scan_reason is None

    @pytest.mark.parametrize(
        "scenario_name",
        [
            "auth_session_list_user_sessions",
            "auth_session_revoke_user_sessions",
            "auth_session_revoke_user_sessions_except",
        ],
    )
    def test_scaled_auth_session_scenarios_require_expiry_index(
        self,
        scenario_name: str,
    ) -> None:
        scenario = next(
            scenario for scenario in STORAGE_SCENARIOS if scenario.name == scenario_name
        )

        expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        assert tuple(index.name for index in expectation.expected_indexes) == (
            "auth_sessions_username_lower_active_expiry_idx",
        )

    def test_people_page_search_and_tags_forbids_large_relation_seq_scans(self) -> None:
        scenario = next(
            scenario
            for scenario in STORAGE_SCENARIOS
            if scenario.name == "people_page_search_and_tags"
        )

        realistic_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.REALISTIC_PROFILE,
        )
        stress_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        expected_forbidden_relations = (
            "knowledge__knowledge_item_model",
            "knowledge__knowledge_item_tag_model",
            "knowledge__person_details_model",
        )
        assert realistic_expectation.forbidden_seq_scan_relations == expected_forbidden_relations
        assert realistic_expectation.allow_seq_scan_reason is None
        assert stress_expectation.forbidden_seq_scan_relations == expected_forbidden_relations
        assert stress_expectation.allow_seq_scan_reason is None
        for query_name in (
            "people_page_search_and_tags__001",
            "people_page_search_and_tags__002",
        ):
            expectation = scenario.plan_expectation(
                policy=ABSOLUTE_SLA_POLICY,
                query_name=query_name,
                profile=query_plan_models.REALISTIC_PROFILE,
            )
            assert {index.name for index in expectation.expected_indexes} == {
                "knowledge_item_tags_author_tag_item_idx",
                "knowledge_items_id_author_uniq",
                "knowledge__person_details_model_pkey",
            }
            stress_query_expectation = scenario.plan_expectation(
                policy=ABSOLUTE_SLA_POLICY,
                query_name=query_name,
                profile=query_plan_models.STRESS_PROFILE,
            )
            assert {index.name for index in stress_query_expectation.expected_indexes} == {
                "knowledge_item_tags_author_tag_item_idx",
                "knowledge__person_details_model_pkey",
                "knowledge__knowledge_item_model_pkey",
            }

    def test_dates_query_plan_scenarios_cover_calendar_and_backlink_indexes(self) -> None:
        calendar = next(
            scenario
            for scenario in STORAGE_SCENARIOS
            if scenario.name == "knowledge_dates_page_calendar"
        )
        backlink = next(
            scenario
            for scenario in STORAGE_SCENARIOS
            if scenario.name == "knowledge_date_ids_for_person"
        )
        search = next(
            scenario
            for scenario in STORAGE_SCENARIOS
            if scenario.name == "knowledge_dates_page_search"
        )

        calendar_page_expectation = calendar.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name="knowledge_dates_page_calendar__001",
            profile=query_plan_models.REALISTIC_PROFILE,
        )
        assert {index.name for index in calendar_page_expectation.expected_indexes} == {
            "date_details_author_calendar_item_idx",
            "knowledge__knowledge_item_model_pkey",
        }
        assert calendar.forbidden_seq_scan_relations == ()
        search_count_expectation = search.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name="knowledge_dates_page_search__002",
            profile=query_plan_models.REALISTIC_PROFILE,
        )
        assert tuple(index.name for index in search_count_expectation.expected_indexes) == (
            "knowledge_items_display_name_trgm_idx",
        )
        assert tuple(index.name for index in backlink.expected_indexes) == (
            "date_people_author_person_date_idx",
        )
        assert backlink.forbidden_seq_scan_relations == (
            "knowledge__date_person_model",
            "knowledge__date_details_model",
        )

    def test_dates_filtered_page_accepts_stress_details_pk_or_composite_index(self) -> None:
        scenario = next(
            scenario
            for scenario in STORAGE_SCENARIOS
            if scenario.name == "knowledge_dates_page_search_tags_person"
        )

        stress_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        assert {index.name for index in stress_expectation.expected_indexes} == {
            "knowledge_item_tags_author_tag_item_idx",
            "date_people_author_person_date_idx",
            "knowledge__knowledge_item_model_pkey",
        }
        assert stress_expectation.forbidden_seq_scan_relations == (
            "knowledge__knowledge_item_model",
            "knowledge__knowledge_item_tag_model",
            "knowledge__date_details_model",
            "knowledge__date_person_model",
        )
        assert stress_expectation.allow_seq_scan_reason is None

    @pytest.mark.parametrize(
        "scenario_name",
        ["knowledge_tags_list", "people_relationship_types_list"],
    )
    def test_full_private_taxonomy_lists_allow_stress_sequential_scan(
        self,
        scenario_name: str,
    ) -> None:
        scenario = next(
            scenario for scenario in STORAGE_SCENARIOS if scenario.name == scenario_name
        )

        realistic_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.REALISTIC_PROFILE,
        )
        stress_expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        assert realistic_expectation.expected_indexes
        assert realistic_expectation.forbidden_seq_scan_relations
        assert stress_expectation.expected_indexes == ()
        assert stress_expectation.forbidden_seq_scan_relations == ()
        assert stress_expectation.allow_seq_scan_reason is not None

    @pytest.mark.parametrize(
        ("scenario_name", "expected_index"),
        [
            ("knowledge_tag_detail", "knowledge_tags_id_author_uniq"),
            ("knowledge_tag_update", "knowledge_tags_id_author_uniq"),
            ("knowledge_tag_delete", "knowledge_tags_id_author_uniq"),
            (
                "people_relationship_type_detail",
                "person_relationship_types_id_author_uniq",
            ),
            (
                "people_relationship_type_update",
                "person_relationship_types_id_author_uniq",
            ),
            (
                "people_relationship_type_delete",
                "person_relationship_types_id_author_uniq",
            ),
        ],
    )
    def test_author_scoped_taxonomy_mutations_require_composite_index(
        self,
        scenario_name: str,
        expected_index: str,
    ) -> None:
        scenario = next(
            scenario for scenario in STORAGE_SCENARIOS if scenario.name == scenario_name
        )

        expectation = scenario.plan_expectation(
            policy=ABSOLUTE_SLA_POLICY,
            query_name=None,
            profile=query_plan_models.STRESS_PROFILE,
        )

        assert tuple(index.name for index in expectation.expected_indexes) == (expected_index,)
