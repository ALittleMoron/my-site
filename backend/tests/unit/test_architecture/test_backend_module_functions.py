import ast
from pathlib import Path


class TestBackendModuleFunctions:
    def test_private_module_functions_are_not_used_in_backend_source(self) -> None:
        source_root = Path(__file__).parents[3] / "src"
        offenders: list[str] = []

        for path in source_root.rglob("*.py"):
            relative_path = path.relative_to(source_root)
            if relative_path.parts[:4] == ("infra", "postgresql", "alembic", "versions"):
                continue
            tree = ast.parse(path.read_text(), filename=str(path))
            offenders.extend(
                f"{relative_path}:{node.lineno}:{node.name}"
                for node in tree.body
                if isinstance(
                    node,
                    ast.FunctionDef | ast.AsyncFunctionDef,
                )
                and node.name.startswith(
                    "_",
                )
            )

        assert offenders == []
