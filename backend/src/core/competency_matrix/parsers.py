from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from pathlib import PurePath
from typing import NoReturn, cast

from core.competency_matrix.exceptions import (
    QuestionQueueImportInvalidError,
    QuestionQueueImportIssue,
)
from core.competency_matrix.readers import QuestionQueueImportExcelReader
from core.competency_matrix.schemas import (
    ParsedQuestionRow,
    QuestionQueueImportFile,
    QuestionQueueImportRules,
    QueuedCompetencyMatrixQuestionCreateParams,
    QueuedCompetencyMatrixQuestionsCreateParams,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class QuestionQueueImportParser:
    rules: QuestionQueueImportRules
    excel_reader: QuestionQueueImportExcelReader

    def parse(
        self,
        *,
        file: QuestionQueueImportFile,
    ) -> QueuedCompetencyMatrixQuestionsCreateParams:
        extension = PurePath(file.filename).suffix.lower()
        if extension in self.rules.unsupported_legacy_excel_extensions:
            self.raise_invalid(
                [self.issue(message=f"Unsupported import file extension: {extension}.", row=None)],
            )
        if extension not in self.supported_extensions():
            self.raise_invalid(
                [
                    self.issue(
                        message=(
                            "Unsupported import file extension. Supported extensions: "
                            f"{', '.join(self.rules.supported_extensions_for_message)}."
                        ),
                        row=None,
                    ),
                ],
            )

        rows = self.parse_rows(file=file, extension=extension)
        issues = self.validate_rows(rows=rows)
        if issues:
            self.raise_invalid(issues)
        return QueuedCompetencyMatrixQuestionsCreateParams(
            questions=[
                QueuedCompetencyMatrixQuestionCreateParams(
                    question=self.normalize_question_text(value=cast("str", row.value)).strip(),
                )
                for row in rows
            ],
        )

    def supported_extensions(self) -> frozenset[str]:
        return self.rules.supported_text_extensions | self.rules.supported_excel_extensions

    def parse_rows(
        self,
        *,
        file: QuestionQueueImportFile,
        extension: str,
    ) -> list[ParsedQuestionRow]:
        if extension == ".txt":
            return self.parse_txt(content=file.content)
        if extension == ".csv":
            return self.parse_csv(content=file.content)
        return self.parse_excel(content=file.content)

    def parse_txt(self, *, content: bytes) -> list[ParsedQuestionRow]:
        text = self.decode_text(content=content)
        return [
            ParsedQuestionRow(row_number=row_number, value=line.strip())
            for row_number, line in enumerate(text.splitlines(), start=1)
        ]

    def parse_csv(self, *, content: bytes) -> list[ParsedQuestionRow]:
        text = self.decode_text(content=content)
        reader = csv.reader(StringIO(text), dialect=self.csv_dialect(text=text))
        rows = list(reader)
        if not rows:
            self.raise_invalid(
                [self.issue(message="Import file must contain at least one question.", row=None)],
            )

        question_column_index = self.question_column_index(header=rows[0])
        return [
            ParsedQuestionRow(
                row_number=row_number,
                value=row[question_column_index] if question_column_index < len(row) else "",
            )
            for row_number, row in enumerate(rows[1:], start=2)
        ]

    def parse_excel(self, *, content: bytes) -> list[ParsedQuestionRow]:
        rows = self.excel_reader.read_rows(content=content)
        if not rows:
            self.raise_invalid(
                [self.issue(message="Import file must contain at least one question.", row=None)],
            )
        question_column_index, first_question_row_index = self.excel_question_column(rows=rows)
        return [
            ParsedQuestionRow(
                row_number=row_number,
                value=row[question_column_index] if question_column_index < len(row) else None,
            )
            for row_number, row in enumerate(
                rows[first_question_row_index:],
                start=first_question_row_index + 1,
            )
        ]

    def decode_text(self, *, content: bytes) -> str:
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError:
            self.raise_invalid(
                [self.issue(message="Import file must be UTF-8 encoded text.", row=None)],
            )

    def csv_dialect(self, *, text: str) -> type[csv.Dialect] | csv.Dialect:
        try:
            return csv.Sniffer().sniff(text[:2048], delimiters=self.rules.csv_delimiters)
        except csv.Error:
            return csv.excel

    def question_column_index(self, *, header: list[str]) -> int:
        for index, value in enumerate(header):
            if value.strip().casefold() in self.rules.question_headers:
                return index
        self.raise_invalid(
            [
                self.issue(
                    message=(
                        "CSV header must contain one of: "
                        f"{', '.join(self.rules.question_headers_for_message)}."
                    ),
                    row=None,
                ),
            ],
        )
        raise AssertionError

    def excel_question_column(self, *, rows: list[tuple[object, ...]]) -> tuple[int, int]:
        for index, value in enumerate(rows[0]):
            if isinstance(value, str) and value.strip().casefold() in self.rules.question_headers:
                return index, 1
        return 0, 0

    def validate_rows(self, *, rows: list[ParsedQuestionRow]) -> list[QuestionQueueImportIssue]:
        issues: list[QuestionQueueImportIssue] = []
        for row in rows:
            if not isinstance(row.value, str):
                issues.append(self.issue(message="Row {row} question must be text.", row=row))
                continue
            question = self.normalize_question_text(value=row.value).strip()
            if not question:
                issues.append(self.issue(message="Row {row} question must not be blank.", row=row))
            elif len(question) > self.rules.question_max_length:
                issues.append(
                    self.issue(
                        message=(
                            "Row {row} question must be at most "
                            f"{self.rules.question_max_length} characters."
                        ),
                        row=row,
                    ),
                )
        if len(rows) == 0:
            issues.append(
                self.issue(message="Import file must contain at least one question.", row=None),
            )
        return issues

    def normalize_question_text(self, *, value: str) -> str:
        return value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

    def issue(
        self,
        *,
        message: str,
        row: ParsedQuestionRow | None,
    ) -> QuestionQueueImportIssue:
        row_number = None if row is None else row.row_number
        return QuestionQueueImportIssue(
            message=message.format(row=row_number),
            row_number=row_number,
        )

    def raise_invalid(self, issues: list[QuestionQueueImportIssue]) -> NoReturn:
        raise QuestionQueueImportInvalidError(issues=issues)
