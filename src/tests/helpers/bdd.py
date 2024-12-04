from typing import Any


class BddHelper:
    @staticmethod
    def assert_equal(actual: Any, expected: Any, msg: str = "") -> None:  # noqa: ANN401
        assert actual == expected, f"{msg}\n{actual=}\n{expected=}"
