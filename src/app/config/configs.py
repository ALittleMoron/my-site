from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, frozen=True, slots=True)
class _DirConstants:
    app: Path = Path(__file__).parent.parent
    src: Path = app.parent
    root: Path = src.parent
    app_templates: Path = app / "templates"
