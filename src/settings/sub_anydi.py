from typing import Any

ANYDI: dict[str, Any] = {
    "CONTAINER_FACTORY": None,
    "STRICT_MODE": True,
    "REGISTER_SETTINGS": False,
    "REGISTER_COMPONENTS": False,
    "INJECT_URLCONF": "urls",
    "MODULES": [
        "api.deps.SharedApiDepsModule",
        "api.competency_matrix.deps.CompetencyMatrixDepsModule",
    ],
    "SCAN_PACKAGES": [],
    "PATCH_NINJA": True,
}
