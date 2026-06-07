import { LanguageCode } from '../../../core/i18n/i18n.model';

export type AdminMatrixGrade = 'Junior' | 'Junior+' | 'Middle' | 'Middle+' | 'Senior';
export type AdminMatrixPublishStatus = 'Draft' | 'Published';

export interface QueuedMatrixQuestionDto {
  id: number;
  question: string;
  grade: AdminMatrixGrade | null;
  sheet: string | null;
  section: string | null;
  subsection: string | null;
  suggestedByUsername: string | null;
  createdAt: string;
}

export interface QueuedMatrixQuestionsDto {
  questions: QueuedMatrixQuestionDto[];
}

export interface QueuedMatrixQuestion {
  id: number;
  question: string;
  grade: AdminMatrixGrade | null;
  sheet: string | null;
  section: string | null;
  subsection: string | null;
  suggestedByUsername: string | null;
  createdAt: string;
}

export interface AdminMatrixItemTranslationPayload {
  question: string;
  answer: string;
  interviewExpectedAnswer: string;
  sheet: string;
  section: string;
  subsection: string;
}

export interface AdminMatrixItemPayload {
  slug: string;
  sheetKey: string;
  grade: AdminMatrixGrade;
  publishStatus: AdminMatrixPublishStatus;
  translations: Record<LanguageCode, AdminMatrixItemTranslationPayload>;
  resources: [];
}

export interface AdminMatrixItemDetailDto {
  id: number;
  slug: string;
  question: string;
}

export function mapQueuedMatrixQuestionDto(dto: QueuedMatrixQuestionDto): QueuedMatrixQuestion {
  return {
    id: dto.id,
    question: dto.question,
    grade: dto.grade,
    sheet: dto.sheet,
    section: dto.section,
    subsection: dto.subsection,
    suggestedByUsername: dto.suggestedByUsername,
    createdAt: dto.createdAt,
  };
}
