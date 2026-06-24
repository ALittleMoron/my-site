import io
from zipfile import ZipFile

from core.i18n.enums import LanguageEnum
from core.resumes.enums import ResumeExportFormatEnum
from core.resumes.schemas import ResumeExportParams
from infra.config.constants import constants
from infra.resume_export.document_exporter import ResumeDocumentExporterImpl
from tests.fixtures import FactoryFixture


class TestResumeExportConstants:
    def test_vendored_font_paths_exist(self) -> None:
        assert constants.resume_export.font_regular_path.is_file()
        assert constants.resume_export.font_bold_path.is_file()
        assert constants.resume_export.font_license_path.is_file()


class TestResumeDocumentExporter(FactoryFixture):
    def test_pdf_export_generates_pdf_bytes(self) -> None:
        exporter = ResumeDocumentExporterImpl(
            font_regular_path=constants.resume_export.font_regular_path,
            font_bold_path=constants.resume_export.font_bold_path,
            font_regular_name=constants.resume_export.font_regular_name,
            font_bold_name=constants.resume_export.font_bold_name,
        )

        document = exporter.export_resume(
            params=ResumeExportParams(
                format=ResumeExportFormatEnum.PDF,
                title="Backend resume",
                language=LanguageEnum.RU,
                content=self.factory.core.resume_content(
                    full_name="Дмитрий Иванов",
                    role="Backend инженер",
                    summary="Строит надежные backend-системы.",
                ),
            ),
        )

        assert document.format == ResumeExportFormatEnum.PDF
        assert document.content.startswith(b"%PDF")

    def test_docx_export_generates_docx_with_resume_text(self) -> None:
        exporter = ResumeDocumentExporterImpl(
            font_regular_path=constants.resume_export.font_regular_path,
            font_bold_path=constants.resume_export.font_bold_path,
            font_regular_name=constants.resume_export.font_regular_name,
            font_bold_name=constants.resume_export.font_bold_name,
        )

        document = exporter.export_resume(
            params=ResumeExportParams(
                format=ResumeExportFormatEnum.DOCX,
                title="Backend resume",
                language=LanguageEnum.EN,
                content=self.factory.core.resume_content(
                    full_name="Candidate Name",
                    role="Backend engineer",
                    summary="Builds reliable backend systems.",
                ),
            ),
        )

        assert document.format == ResumeExportFormatEnum.DOCX
        with ZipFile(io.BytesIO(document.content)) as archive:
            document_xml = archive.read("word/document.xml").decode()
        assert "Candidate Name" in document_xml
        assert "Builds reliable backend systems." in document_xml
