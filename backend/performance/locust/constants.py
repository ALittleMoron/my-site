class HttpConstants:
    ok: int = 200
    no_content: int = 204
    too_many_requests: int = 429


class WaitTimeConstants:
    min_seconds: float = 0.2
    max_seconds: float = 1.0


class TaskWeightConstants:
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


class ArticlesConstants:
    discovery_page_size: int = 100
    list_page_size: int = 10


class SeedConstants:
    entity_prefix: str = "perf-seed-"


class MatrixQuestionSuggestionConstants:
    prefix: str = "Locust matrix suggestion"
    success_statuses: frozenset[int] = frozenset(
        {HttpConstants.no_content, HttpConstants.too_many_requests},
    )


class Constants:
    http: HttpConstants = HttpConstants()
    wait_time: WaitTimeConstants = WaitTimeConstants()
    task_weights: TaskWeightConstants = TaskWeightConstants()
    articles: ArticlesConstants = ArticlesConstants()
    seed: SeedConstants = SeedConstants()
    matrix_question_suggestion: MatrixQuestionSuggestionConstants = (
        MatrixQuestionSuggestionConstants()
    )


constants = Constants()
