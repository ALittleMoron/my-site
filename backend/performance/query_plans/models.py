from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

JsonObject = Mapping[str, object]
DatabaseParams = Mapping[str, object] | tuple[object, ...]


class QueryThresholdGroup(StrEnum):
    POINT_READ = "point_read"
    LIST_READ = "list_read"
    SEARCH = "search"
    AGGREGATE = "aggregate"
    SMALL_WRITE = "small_write"
    HEAVY = "heavy"


@dataclass(frozen=True, slots=True)
class DatasetProfile:
    name: str
    article_count: int
    tag_count: int
    article_tag_link_count: int
    resource_count: int
    explain_runs: int


@dataclass(frozen=True, slots=True)
class PlanExpectation:
    max_execution_ms: float
    threshold_source: str
    expected_index_names: tuple[str, ...]
    forbidden_seq_scan_relations: tuple[str, ...]
    allow_seq_scan_reason: str | None


@dataclass(frozen=True, slots=True)
class CapturedQuery:
    name: str
    storage_class: str
    method_name: str
    scenario_name: str
    ordinal: int
    sql: str
    normalized_sql: str
    params: DatabaseParams
    elapsed_ms: float
    executemany: bool
    expectation: PlanExpectation


@dataclass(frozen=True, slots=True)
class CompiledQuery:
    name: str
    sql: str
    params: DatabaseParams


@dataclass(frozen=True, slots=True)
class PlanAnalysis:
    name: str
    planning_time_ms: float
    execution_time_ms: float
    node_types: tuple[str, ...]
    index_names: tuple[str, ...]
    seq_scan_relations: tuple[str, ...]
    temp_blocks: int
    findings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    query: CapturedQuery
    compiled_query: CompiledQuery
    explain_json_runs: tuple[object, ...]
    analyses: tuple[PlanAnalysis, ...]
    warm_execution_ms: float
    findings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StorageMethod:
    storage_class: str
    method_name: str
    module_name: str


@dataclass(frozen=True, slots=True)
class CoverageReport:
    discovered_methods: tuple[StorageMethod, ...]
    covered_methods: tuple[StorageMethod, ...]
    missing_methods: tuple[StorageMethod, ...]
    unexpected_methods: tuple[StorageMethod, ...]


@dataclass(frozen=True, slots=True)
class CliArgs:
    profile: str
    report_dir: Path
    fail_on_finding: bool
    allow_non_test_db: bool


BALANCED_PROFILE = DatasetProfile(
    name="balanced",
    article_count=200_000,
    tag_count=30_000,
    article_tag_link_count=500_000,
    resource_count=200_000,
    explain_runs=3,
)
