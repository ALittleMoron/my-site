import tomllib
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[3]


class TestGranianRuntimeContract:
    def test_backend_declares_granian_without_direct_uvicorn_dependency(self) -> None:
        pyproject = tomllib.loads((BACKEND_ROOT / "pyproject.toml").read_text())
        dependencies = pyproject["project"]["dependencies"]

        assert "granian[reload]>=2.7.7" in dependencies
        assert [dependency for dependency in dependencies if dependency.startswith("uvicorn")] == []

    def test_backend_runtime_entrypoints_use_granian_asgi_factory(self) -> None:
        production_command = (
            "granian --interface asgi --factory --host 0.0.0.0 --port 8080 main:create_app"
        )
        local_command = (
            "granian --interface asgi --factory --host localhost --port 8000 "
            "--reload main:create_app"
        )
        performance_command = (
            'granian --interface asgi --factory --host 127.0.0.1 --port "$port" main:create_app'
        )

        assert production_command in (BACKEND_ROOT / "start_application.sh").read_text()
        assert production_command in (BACKEND_ROOT / "scripts/app.sh").read_text()
        assert local_command in (BACKEND_ROOT / "scripts/app.sh").read_text()
        assert performance_command in (BACKEND_ROOT / "scripts/run_locust.sh").read_text()

    def test_main_module_exposes_only_litestar_app_factory(self) -> None:
        main_source = (BACKEND_ROOT / "src/main.py").read_text()

        assert "def create_app()" in main_source
        assert "uvicorn" not in main_source
        assert "__main__" not in main_source
