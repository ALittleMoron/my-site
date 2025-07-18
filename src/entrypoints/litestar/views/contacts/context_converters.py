from dataclasses import dataclass
from typing import Any, Literal


@dataclass(kw_only=True, frozen=True, slots=True)
class ContactsContextConverter:
    def alert_context(
        self,
        alert_type: Literal["success", "danger", "warning", "info"],
        message: str,
    ) -> dict[str, Any]:
        return {"alert_type": alert_type, "message": message}
