from dataclasses import dataclass

from ninja.testing.client import NinjaResponse

from tests.client import SyncAndAsyncNinjaClient


@dataclass(kw_only=True, frozen=True, slots=True)
class APIHelper:
    client: SyncAndAsyncNinjaClient

    def get_health(self) -> NinjaResponse:
        return self.client.get("/health")

    def get_competency_matrix_sheets(self) -> NinjaResponse:
        return self.client.get("/competency-matrix/sheets/")

    def get_competency_matrix_items(self, sheet_name: str = "") -> NinjaResponse:
        return self.client.get(f"/competency-matrix/items/?sheetName={sheet_name}")
