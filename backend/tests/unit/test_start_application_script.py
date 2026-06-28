import os
import shutil
import stat
import subprocess
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = BACKEND_ROOT / "start_application.sh"


def test_init_action_skips_owner_creation_when_owner_init_disabled(tmp_path: Path) -> None:
    result, commands = _run_init_action(tmp_path=tmp_path, owner_init_enabled="false")

    assert result.returncode == 0, result.stderr
    assert commands == [
        "alembic -c src/infra/postgresql/alembic/alembic.ini upgrade head",
        "litestar invalidatecache",
        "litestar initbuckets",
    ]


def test_init_action_creates_owner_when_owner_init_enabled(tmp_path: Path) -> None:
    result, commands = _run_init_action(tmp_path=tmp_path, owner_init_enabled="true")

    assert result.returncode == 0, result.stderr
    assert commands == [
        "alembic -c src/infra/postgresql/alembic/alembic.ini upgrade head",
        "litestar invalidatecache",
        "litestar initbuckets",
        "litestar createsuperuser --username owner --password owner-password",
    ]


def test_init_action_rejects_invalid_owner_init_enabled_values(tmp_path: Path) -> None:
    result, commands = _run_init_action(tmp_path=tmp_path, owner_init_enabled="yes")

    assert result.returncode == 2
    assert result.stderr == "OWNER_INIT_ENABLED must be true or false\n"
    assert commands == []


def _run_init_action(
    *,
    tmp_path: Path,
    owner_init_enabled: str,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_path = tmp_path / "commands.log"
    _write_command_stub(
        path=bin_dir / "alembic",
        command_name="alembic",
        log_path=log_path,
    )
    _write_command_stub(
        path=bin_dir / "litestar",
        command_name="litestar",
        log_path=log_path,
    )
    bash_path = shutil.which("bash")
    assert bash_path is not None

    env = {
        "OWNER_INIT_ENABLED": owner_init_enabled,
        "OWNER_INIT_LOGIN": "owner",
        "OWNER_INIT_PASSWORD": "owner-password",
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
    }
    result = subprocess.run(  # noqa: S603
        [bash_path, str(SCRIPT_PATH), "init"],
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if not log_path.exists():
        return result, []
    return result, log_path.read_text(encoding="utf-8").splitlines()


def _write_command_stub(*, path: Path, command_name: str, log_path: Path) -> None:
    path.write_text(
        f'#!/usr/bin/env bash\nprintf "{command_name} %s\\n" "$*" >> "{log_path}"\n',
        encoding="utf-8",
    )
    path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
