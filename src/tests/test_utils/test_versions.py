import pytest
from pytest_mock import MockerFixture

from app.core_utils import get_app_version


@pytest.mark.parametrize(
    "expected_version",
    ["0.0.1", "0.1.1", "1.1.1", "1.1.0", "1.0.0", "0.0.0"],
)
def test_get_app_version(mocker: MockerFixture, expected_version: str):
    mocker.patch('tomllib.load', return_value={"project": {"version": expected_version}})
    assert get_app_version() == expected_version


def test_get_app_version_incorrect_toml_data(mocker: MockerFixture):
    mocker.patch('tomllib.load', return_value={})
    assert get_app_version() == "1.0.0"
