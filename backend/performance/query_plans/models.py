from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Select

JsonObject = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class DatasetProfile:
    name: str
    note_count: int
    tag_count: int
    note_tag_link_count: int
    resource_count: int
    explain_runs: int


@dataclass(frozen=True, slots=True)
class PlanExpectation:
    max_execution_ms: float
    expected_index_names: tuple[str, ...]
    forbidden_seq_scan_relations: tuple[str, ...]
    allow_seq_scan_reason: str | None


@dataclass(frozen=True, slots=True)
class CapturedQuery:
    name: str
    statement: Select[tuple[object, ...]]
    expectation: PlanExpectation


@dataclass(frozen=True, slots=True)
class CompiledQuery:
    name: str
    sql: str
    params: Mapping[str, object]


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
class CliArgs:
    profile: str
    report_dir: Path
    fail_on_finding: bool
    allow_non_test_db: bool


BALANCED_PROFILE = DatasetProfile(
    name="balanced",
    note_count=200_000,
    tag_count=30_000,
    note_tag_link_count=500_000,
    resource_count=200_000,
    explain_runs=3,
)
