from collections.abc import Awaitable, Callable
from dataclasses import dataclass

type PostCommitAction = Callable[[], Awaitable[None]]


@dataclass(kw_only=True, slots=True)
class PostCommitActions:
    actions: list[PostCommitAction]

    def add(self, *, action: PostCommitAction) -> None:
        self.actions.append(action)

    async def run(self) -> None:
        for action in self.actions:
            await action()
