from collections.abc import Iterator, Mapping, Sequence
from typing import cast

from performance.query_plans.models import JsonObject, PlanAnalysis, PlanExpectation


def analyze_explain_result(
    *,
    name: str,
    explain_json: Sequence[object],
    expectation: PlanExpectation,
) -> PlanAnalysis:
    raw_entry = cast("JsonObject", explain_json[0])
    plan = cast("JsonObject", raw_entry["Plan"])
    analysis = analyze_plan_shape(
        name=name,
        plan=plan,
        planning_time_ms=float(cast("int | float", raw_entry.get("Planning Time", 0.0))),
        execution_time_ms=float(cast("int | float", raw_entry.get("Execution Time", 0.0))),
    )
    return PlanAnalysis(
        name=analysis.name,
        planning_time_ms=analysis.planning_time_ms,
        execution_time_ms=analysis.execution_time_ms,
        node_types=analysis.node_types,
        index_names=analysis.index_names,
        seq_scan_relations=analysis.seq_scan_relations,
        temp_blocks=analysis.temp_blocks,
        findings=evaluate_plan_analysis(
            analysis=analysis,
            expectation=expectation,
            measured_execution_ms=analysis.execution_time_ms,
        ),
    )


def analyze_plan_shape(
    *,
    name: str,
    plan: JsonObject,
    planning_time_ms: float,
    execution_time_ms: float,
) -> PlanAnalysis:
    nodes = tuple(iter_plan_nodes(plan))
    return PlanAnalysis(
        name=name,
        planning_time_ms=planning_time_ms,
        execution_time_ms=execution_time_ms,
        node_types=tuple(read_text_value(node=node, key="Node Type") for node in nodes),
        index_names=tuple(
            index_name
            for node in nodes
            if (index_name := read_optional_text_value(node=node, key="Index Name")) is not None
        ),
        seq_scan_relations=tuple(
            relation_name
            for node in nodes
            if read_text_value(node=node, key="Node Type") == "Seq Scan"
            if (relation_name := read_optional_text_value(node=node, key="Relation Name"))
            is not None
        ),
        temp_blocks=sum(read_int_value(node=node, key="Temp Read Blocks") for node in nodes)
        + sum(read_int_value(node=node, key="Temp Written Blocks") for node in nodes),
        findings=(),
    )


def evaluate_plan_analysis(
    *,
    analysis: PlanAnalysis,
    expectation: PlanExpectation,
    measured_execution_ms: float,
) -> tuple[str, ...]:
    findings = [
        f"missing expected index {expected_index}"
        for expected_index in expectation.expected_index_names
        if expected_index not in analysis.index_names
    ]
    if expectation.allow_seq_scan_reason is None:
        findings.extend(
            f"Seq Scan on {relation_name}"
            for relation_name in expectation.forbidden_seq_scan_relations
            if relation_name in analysis.seq_scan_relations
        )
    if measured_execution_ms > expectation.max_execution_ms:
        findings.append(
            f"execution time {measured_execution_ms:.2f} ms exceeded "
            f"{expectation.max_execution_ms:.2f} ms",
        )
    if analysis.temp_blocks > 0:
        findings.append(f"query used {analysis.temp_blocks} temp blocks")
    return tuple(findings)


def iter_plan_nodes(plan: JsonObject) -> Iterator[JsonObject]:
    yield plan
    raw_children = plan.get("Plans", ())
    if isinstance(raw_children, Sequence) and not isinstance(raw_children, str):
        for child in raw_children:
            if isinstance(child, Mapping):
                yield from iter_plan_nodes(cast("JsonObject", child))


def read_text_value(*, node: JsonObject, key: str) -> str:
    value = read_optional_text_value(node=node, key=key)
    if value is None:
        msg = f"Plan node is missing {key}"
        raise ValueError(msg)
    return value


def read_optional_text_value(*, node: JsonObject, key: str) -> str | None:
    value = node.get(key)
    return value if isinstance(value, str) else None


def read_int_value(*, node: JsonObject, key: str) -> int:
    value = node.get(key)
    return int(cast("int | float", value)) if isinstance(value, int | float) else 0
