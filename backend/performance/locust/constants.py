class _HttpConstants:
    ok: int = 200
    no_content: int = 204
    too_many_requests: int = 429


class _WaitTimeConstants:
    min_seconds: float = 0.2
    max_seconds: float = 1.0


class _TaskWeightConstants:
    healthcheck: int = 2
    i18n_languages: int = 2
    i18n_bundle: int = 2
    articles_list: int = 4
    articles_tree: int = 2
    article_detail: int = 3
    matrix_sheets: int = 3
    matrix_items: int = 3
    matrix_item_detail: int = 3
    matrix_question_suggestion: int = 1
    spa_root: int = 1


class _ArticlesConstants:
    discovery_page_size: int = 100
    list_page_size: int = 10


class _SeedConstants:
    entity_prefix: str = "perf-seed-"


class _MatrixQuestionSuggestionConstants:
    prefix: str = "Locust matrix suggestion"
    success_statuses: frozenset[int] = frozenset(
        {_HttpConstants.no_content, _HttpConstants.too_many_requests},
    )


class Constants:
    http: _HttpConstants = _HttpConstants()
    wait_time: _WaitTimeConstants = _WaitTimeConstants()
    task_weights: _TaskWeightConstants = _TaskWeightConstants()
    articles: _ArticlesConstants = _ArticlesConstants()
    seed: _SeedConstants = _SeedConstants()
    matrix_question_suggestion: _MatrixQuestionSuggestionConstants = (
        _MatrixQuestionSuggestionConstants()
    )


constants = Constants()
