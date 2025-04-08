import anydi

from db.storages import CompetencyMatrixDatabaseStorage, CompetencyMatrixStorage


class SharedApiDepsModule(anydi.Module):
    @anydi.provider(scope="singleton")
    def database_deps(self) -> CompetencyMatrixStorage:
        return CompetencyMatrixDatabaseStorage()
