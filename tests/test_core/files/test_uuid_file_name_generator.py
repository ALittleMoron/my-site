import uuid
from unittest.mock import Mock

import pytest

from core.files.file_name_generators import UUIDFileNameGenerator


class TestUUIDFileNameGenerator:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.uuid_generator = UUIDFileNameGenerator()
        self.fixed_uuid = uuid.UUID("12345678-1234-5678-9abc-def012345678")
        self.mock_uuid_generator = Mock(return_value=self.fixed_uuid)
        self.custom_uuid_generator = UUIDFileNameGenerator(generator=self.mock_uuid_generator)

    def test_generate_file_name_without_folder(self) -> None:
        file_name = self.uuid_generator()

        assert isinstance(file_name, str)
        assert len(file_name) == 32  # UUID hex без дефисов
        assert all(c in "0123456789abcdef" for c in file_name)

    @pytest.mark.parametrize(
        "folder,expected_prefix",
        [
            ("uploads", "uploads/"),
            ("uploads/images", "uploads/images/"),
            ("", ""),
            ("/uploads/", "uploads/"),
            ("/folder/subfolder/", "folder/subfolder/"),
        ],
    )
    def test_generate_file_name_with_folder(self, folder: str, expected_prefix: str) -> None:
        file_name = self.uuid_generator(folder=folder)

        if expected_prefix:
            assert file_name.startswith(expected_prefix)
        else:
            assert not file_name.startswith("/")

        assert len(file_name.split("/")[-1]) == 32

    def test_custom_uuid_generator(self) -> None:
        file_name = self.custom_uuid_generator()

        assert file_name == "12345678123456789abcdef012345678"
        self.mock_uuid_generator.assert_called_once()

    def test_multiple_calls_generate_different_names(self) -> None:
        file_names = [self.uuid_generator() for _ in range(10)]

        assert len(set(file_names)) == 10

    def test_file_name_is_valid_hex(self) -> None:
        file_name = self.uuid_generator()

        assert all(c in "0123456789abcdef" for c in file_name)
        assert len(file_name) == 32

    @pytest.mark.parametrize(
        "input_folder,expected_prefix",
        [
            ("folder", "folder/"),
            ("/folder", "folder/"),
            ("folder/", "folder/"),
            ("/folder/", "folder/"),
            ("folder/subfolder", "folder/subfolder/"),
            ("/folder/subfolder/", "folder/subfolder/"),
        ],
    )
    def test_folder_handling_edge_cases(self, input_folder: str, expected_prefix: str) -> None:
        file_name = self.uuid_generator(folder=input_folder)
        assert file_name.startswith(expected_prefix)
        assert len(file_name.split("/")[-1]) == 32

    def test_generator_is_callable(self) -> None:
        assert callable(self.uuid_generator)
        file_name = self.uuid_generator()
        assert isinstance(file_name, str)
