import json
from enum import Enum

from sqlalchemy.engine import Dialect
from sqlalchemy.ext.asyncio import AsyncConnection

from performance.query_plans.models import CapturedQuery, CompiledQuery

EXPLAIN_PREFIX = "EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) "


def compile_captured_query(*, query: CapturedQuery, dialect: Dialect) -> CompiledQuery:
    compiled = query.statement.compile(
        dialect=dialect,
        compile_kwargs={"render_postcompile": True},
    )
    return CompiledQuery(
        name=query.name,
        sql=str(compiled),
        params={key: normalize_database_param(value) for key, value in compiled.params.items()},
    )


def normalize_database_param(value: object) -> object:
    if isinstance(value, Enum):
        return value.name
    return value


async def run_explain(*, connection: AsyncConnection, compiled_query: CompiledQuery) -> object:
    result = await connection.exec_driver_sql(
        f"{EXPLAIN_PREFIX}{compiled_query.sql}",
        compiled_query.params,
    )
    row = result.first()
    if row is None:
        msg = f"EXPLAIN returned no rows for {compiled_query.name}"
        raise RuntimeError(msg)
    raw_plan = row[0]
    return json.loads(raw_plan) if isinstance(raw_plan, str) else raw_plan
