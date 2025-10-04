import time
from unittest.mock import Mock

import pytest

from core.files.file_name_generators import TimestampFileNameGenerator


class TestTimestampFileNameGenerator:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.timestamp_generator = TimestampFileNameGenerator()
        self.custom_length_generator = TimestampFileNameGenerator(random_suffix_length=6)
        self.mock_generator = Mock(return_value="abc123")
        self.custom_generator = TimestampFileNameGenerator(random_generator=self.mock_generator)

    def test_generate_file_name_without_folder(self) -> None:
        file_name = self.timestamp_generator()

        assert isinstance(file_name, str)
        assert "_" in file_name
        parts = file_name.split("_")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[1]) == 8  # 4 bytes * 2 hex chars

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
        file_name = self.timestamp_generator(folder=folder)

        if expected_prefix:
            assert file_name.startswith(expected_prefix)
        else:
            assert not file_name.startswith("/")

        assert "_" in file_name
        parts = file_name.split("/")[-1].split("_")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[1]) == 8

    def test_custom_random_suffix_length(self) -> None:
        file_name = self.custom_length_generator()

        parts = file_name.split("_")
        assert len(parts[1]) == 12  # 6 bytes * 2 hex chars

    def test_custom_random_generator(self) -> None:
        file_name = self.custom_generator()

        parts = file_name.split("_")
        assert parts[1] == "abc123"
        self.mock_generator.assert_called_once_with(4)

    def test_timestamp_increases_over_time(self) -> None:
        file_name1 = self.timestamp_generator()
        time.sleep(0.001)  # 1 миллисекунда
        file_name2 = self.timestamp_generator()

        timestamp1 = int(file_name1.split("_")[0])
        timestamp2 = int(file_name2.split("_")[0])

        assert timestamp2 > timestamp1

    def test_multiple_calls_generate_different_names(self) -> None:
        file_names = [self.timestamp_generator() for _ in range(10)]

        assert len(set(file_names)) == 10

    def test_file_name_format(self) -> None:
        file_name = self.timestamp_generator()

        parts = file_name.split("_")
        timestamp_part = parts[0]
        random_part = parts[1]

        assert len(timestamp_part) >= 13  # минимум для микросекунд
        assert timestamp_part.isdigit()
        assert len(random_part) == 8
        assert all(c in "0123456789abcdef" for c in random_part)
