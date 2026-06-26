import { LanguageCode } from '../../../core/i18n/i18n.model';
import {
  ReadonlyMatrixQuestionList,
  ReadonlyMatrixSheet,
} from '../../../shared/ui/matrix-readonly.model';

export type AdminMatrixGrade = 'Junior' | 'Junior+' | 'Middle' | 'Middle+' | 'Senior';
export type AdminMatrixInterviewFrequency = 'constantly' | 'often' | 'rarely' | 'neverSeen';
export type AdminMatrixPublishStatus = 'Draft' | 'Published';
export type AdminMatrixWorkspaceSort =
  | 'grade'
  | 'interviewFrequency'
  | 'section'
  | 'subsection'
  | 'newest'
  | 'oldest'
  | 'missingFields'
  | 'dangerousPublished';
export type AdminMatrixMissingField =
  | 'slug'
  | 'grade'
  | 'questionRu'
  | 'questionEn'
  | 'answerRu'
  | 'answerEn'
  | 'interviewExpectedAnswerRu'
  | 'interviewExpectedAnswerEn';

export const ADMIN_MATRIX_PUBLICATION_FIELDS: readonly AdminMatrixMissingField[] = [
  'slug',
  'grade',
  'questionRu',
  'questionEn',
  'answerRu',
  'answerEn',
  'interviewExpectedAnswerRu',
  'interviewExpectedAnswerEn',
];

export type AdminReadonlyMatrixSheet = ReadonlyMatrixSheet;
export type AdminReadonlyMatrixQuestionList = ReadonlyMatrixQuestionList;

export interface AdminMatrixQuestionWorkspaceFilters {
  page: number;
  pageSize: number;
  language: LanguageCode;
  sort: AdminMatrixWorkspaceSort;
  searchQuery?: string;
  sheetKeys?: string[];
  grades?: AdminMatrixGrade[];
  interviewFrequencies?: AdminMatrixInterviewFrequency[];
  sections?: string[];
  subsections?: string[];
  publishStatuses?: AdminMatrixPublishStatus[];
  publishedFrom?: string;
  publishedTo?: string;
  hasMissingFields?: boolean;
}

export interface AdminMatrixWorkspaceSummary {
  total: number;
  draft: number;
  missingDraft: number;
  dangerousPublished: number;
  readyPublished: number;
}

export interface AdminMatrixWorkspaceItem {
  id: string;
  slug: string;
  question: string;
  sheetKey: string;
  sheet: string;
  grade: AdminMatrixGrade | null;
  interviewFrequency: AdminMatrixInterviewFrequency | null;
  section: string;
  subsection: string;
  publishStatus: AdminMatrixPublishStatus;
  publishedAt: string | null;
  missingFields: AdminMatrixMissingField[];
}

export interface AdminMatrixQuestionWorkspace {
  totalCount: number;
  totalPages: number;
  summary: AdminMatrixWorkspaceSummary;
  items: AdminMatrixWorkspaceItem[];
}

export interface AdminMatrixFilterOption {
  key: string;
  label: string;
}

export interface AdminMatrixFilterSectionOption {
  label: string;
  subsections: string[];
}

export interface AdminMatrixFilterSheetOption extends AdminMatrixFilterOption {
  sections: AdminMatrixFilterSectionOption[];
}

export interface AdminMatrixWorkspaceFilterOptions {
  sheets: AdminMatrixFilterSheetOption[];
  grades: AdminMatrixGrade[];
  interviewFrequencies: AdminMatrixInterviewFrequency[];
  sections: string[];
  subsections: string[];
  publishStatuses: AdminMatrixPublishStatus[];
}

export interface AdminMatrixQuestionTranslation {
  question: string;
  answer: string;
  interviewExpectedAnswer: string;
}

export interface AdminMatrixQuestionTranslations {
  ru: AdminMatrixQuestionTranslation;
  en: AdminMatrixQuestionTranslation;
}

export interface AdminMatrixAttachedResourceDto {
  id: number;
  name: string;
  url: string;
  context: string;
  translations: {
    ru: { name: string; context: string };
    en: { name: string; context: string };
  };
}

export interface AdminMatrixQuestionDetailDto {
  id: string;
  slug: string;
  question: string;
  answer: string;
  interviewExpectedAnswer: string;
  subsectionId: number;
  sheetKey: string;
  sheet: string;
  grade: AdminMatrixGrade | null;
  interviewFrequency: AdminMatrixInterviewFrequency | null;
  section: string;
  subsection: string;
  publishStatus: AdminMatrixPublishStatus;
  translations: AdminMatrixQuestionTranslations;
  resources: AdminMatrixAttachedResourceDto[];
}

export interface AdminMatrixExistingResourceAttachmentPayload {
  resourceId: number;
  translations: {
    ru: { context: string };
    en: { context: string };
  };
}

export interface AdminMatrixResourceTranslation {
  name: string;
}

export interface AdminMatrixResourceTranslations {
  ru: AdminMatrixResourceTranslation;
  en: AdminMatrixResourceTranslation;
}

export interface AdminMatrixResource {
  id: number;
  name: string;
  url: string;
  translations: AdminMatrixResourceTranslations;
}

export interface AdminMatrixResourcesDto {
  resources: AdminMatrixResource[];
}

export interface AdminMatrixNewResourcePayload {
  url: string;
  translations: AdminMatrixResourceTranslations;
}

export interface AdminMatrixNewResourceAttachmentPayload {
  resource: AdminMatrixNewResourcePayload;
  translations: {
    ru: { context: string };
    en: { context: string };
  };
}

export type AdminMatrixResourceAttachmentPayload =
  | AdminMatrixExistingResourceAttachmentPayload
  | AdminMatrixNewResourceAttachmentPayload;

export interface AdminMatrixQuestionPayload {
  slug: string;
  subsectionId: number;
  grade: AdminMatrixGrade | null;
  interviewFrequency: AdminMatrixInterviewFrequency | null;
  publishStatus: AdminMatrixPublishStatus;
  translations: AdminMatrixQuestionTranslations;
  resources: AdminMatrixResourceAttachmentPayload[];
}

export interface AdminMatrixStructureNameTranslation {
  name: string;
}

export interface AdminMatrixStructureNameTranslations {
  ru: AdminMatrixStructureNameTranslation;
  en: AdminMatrixStructureNameTranslation;
}

export interface AdminMatrixStructureSubsection {
  id: number;
  name: string;
  translations: AdminMatrixStructureNameTranslations;
}

export interface AdminMatrixStructureSection {
  id: number;
  name: string;
  translations: AdminMatrixStructureNameTranslations;
  subsections: AdminMatrixStructureSubsection[];
}

export interface AdminMatrixStructureSheet {
  id: number;
  key: string;
  name: string;
  translations: AdminMatrixStructureNameTranslations;
  sections: AdminMatrixStructureSection[];
}

export interface AdminMatrixStructure {
  sheets: AdminMatrixStructureSheet[];
}

export interface AdminMatrixSheetCreatePayload {
  key: string;
  translations: AdminMatrixStructureNameTranslations;
}

export interface AdminMatrixSectionCreatePayload {
  translations: AdminMatrixStructureNameTranslations;
}

export interface AdminMatrixSubsectionCreatePayload {
  translations: AdminMatrixStructureNameTranslations;
}

export interface MatrixSheetDto {
  key: string;
  name: string;
}

export interface MatrixSheetsDto {
  sheets: MatrixSheetDto[];
}

export interface MatrixItemDto {
  slug: string;
  question: string;
  interviewFrequency: AdminMatrixInterviewFrequency | null;
}

export interface MatrixGradeGroupDto {
  grade: AdminMatrixGrade | null;
  items: MatrixItemDto[];
}

export interface MatrixSubsectionGroupDto {
  subsection: string;
  grades: MatrixGradeGroupDto[];
}

export interface MatrixSectionGroupDto {
  section: string;
  subsections: MatrixSubsectionGroupDto[];
}

export interface MatrixItemsListDto {
  sheetKey: string;
  sheet: string;
  sections: MatrixSectionGroupDto[];
}

export type AdminMatrixWorkspaceDto = AdminMatrixQuestionWorkspace;

export type AdminMatrixWorkspaceFilterOptionsDto = AdminMatrixWorkspaceFilterOptions;

export function mapPublicSheetsDto(dto: MatrixSheetsDto): AdminReadonlyMatrixSheet[] {
  return dto.sheets.map((sheet) => ({ key: sheet.key, name: sheet.name }));
}

export function mapPublicQuestionsDto(dto: MatrixItemsListDto): AdminReadonlyMatrixQuestionList {
  return {
    sheetKey: dto.sheetKey,
    sheet: dto.sheet,
    sections: dto.sections.map((section) => ({
      section: section.section,
      subsections: section.subsections.map((subsection) => ({
        subsection: subsection.subsection,
        grades: subsection.grades.map((grade) => ({
          grade: grade.grade,
          questions: grade.items.map((item) => ({
            slug: item.slug,
            question: item.question,
            interviewFrequency: item.interviewFrequency,
          })),
        })),
      })),
    })),
  };
}

export function mapResourcePayloads(
  detail: AdminMatrixQuestionDetailDto,
): AdminMatrixExistingResourceAttachmentPayload[] {
  return detail.resources.map((resource) => ({
    resourceId: resource.id,
    translations: {
      ru: { context: resource.translations.ru.context },
      en: { context: resource.translations.en.context },
    },
  }));
}

export function buildMatrixQuestionPayloadFromDetail(
  detail: AdminMatrixQuestionDetailDto,
): AdminMatrixQuestionPayload {
  return {
    slug: detail.slug,
    subsectionId: detail.subsectionId,
    grade: detail.grade,
    interviewFrequency: detail.interviewFrequency,
    publishStatus: detail.publishStatus,
    translations: detail.translations,
    resources: mapResourcePayloads(detail),
  };
}

export function missingMatrixQuestionPayloadFields(
  payload: AdminMatrixQuestionPayload,
): AdminMatrixMissingField[] {
  return ADMIN_MATRIX_PUBLICATION_FIELDS.filter((field) =>
    isMatrixQuestionPayloadFieldMissing(payload, field),
  );
}

function isMatrixQuestionPayloadFieldMissing(
  payload: AdminMatrixQuestionPayload,
  field: AdminMatrixMissingField,
): boolean {
  switch (field) {
    case 'slug':
      return payload.slug.trim() === '';
    case 'grade':
      return payload.grade === null;
    case 'questionRu':
      return payload.translations.ru.question.trim() === '';
    case 'questionEn':
      return payload.translations.en.question.trim() === '';
    case 'answerRu':
      return payload.translations.ru.answer.trim() === '';
    case 'answerEn':
      return payload.translations.en.answer.trim() === '';
    case 'interviewExpectedAnswerRu':
      return payload.translations.ru.interviewExpectedAnswer.trim() === '';
    case 'interviewExpectedAnswerEn':
      return payload.translations.en.interviewExpectedAnswer.trim() === '';
  }
}
