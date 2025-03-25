from core.competency_matrix.schemas import Resource


class FactoryHelper:

    @classmethod
    def resource(
        cls,
        resource_id: int,
        name: str = "RESOURCE",
        url: str = "https://example.com",
        context: str = "Context",
    ) -> Resource:
        return Resource(
            id=resource_id,
            name=name,
            url=url,
            context=context,
        )
