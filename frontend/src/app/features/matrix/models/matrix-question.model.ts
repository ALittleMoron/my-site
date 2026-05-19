export interface MatrixResourceDto {
  id: number;
  name: string;
  url: string;
  context: string;
}

export interface MatrixItemDto {
  id: number;
  question: string;
}

export interface MatrixItemDetailDto extends MatrixItemDto {
  answer: string;
  interviewExpectedAnswer: string;
  sheet: string;
  grade: string | null;
  section: string;
  subsection: string;
  publishStatus: 'Draft' | 'Published';
  resources: MatrixResourceDto[];
}

export interface MatrixGradeGroupDto {
  grade: string;
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
  sheet: string;
  sections: MatrixSectionGroupDto[];
}

export interface MatrixSheetsDto {
  sheets: string[];
}

export interface MatrixResource {
  id: number;
  name: string;
  url: string;
  context: string;
}

export interface MatrixQuestion {
  id: number;
  question: string;
}

export interface MatrixQuestionDetail extends MatrixQuestion {
  answer: string;
  interviewExpectedAnswer: string;
  sheet: string;
  grade: string | null;
  section: string;
  subsection: string;
  publishStatus: 'Draft' | 'Published';
  resources: MatrixResource[];
}

export interface MatrixGradeGroup {
  grade: string;
  questions: MatrixQuestion[];
}

export interface MatrixSubsectionGroup {
  subsection: string;
  grades: MatrixGradeGroup[];
}

export interface MatrixSectionGroup {
  section: string;
  subsections: MatrixSubsectionGroup[];
}

export interface MatrixQuestionList {
  sheet: string;
  sections: MatrixSectionGroup[];
}

export function mapMatrixListDto(dto: MatrixItemsListDto): MatrixQuestionList {
  return {
    sheet: dto.sheet,
    sections: dto.sections.map(section => ({
      section: section.section,
      subsections: section.subsections.map(subsection => ({
        subsection: subsection.subsection,
        grades: subsection.grades.map(grade => ({
          grade: grade.grade,
          questions: grade.items.map(item => ({
            id: item.id,
            question: item.question,
          })),
        })),
      })),
    })),
  };
}

export function mapMatrixDetailDto(dto: MatrixItemDetailDto): MatrixQuestionDetail {
  return {
    id: dto.id,
    question: dto.question,
    answer: dto.answer,
    interviewExpectedAnswer: dto.interviewExpectedAnswer,
    sheet: dto.sheet,
    grade: dto.grade,
    section: dto.section,
    subsection: dto.subsection,
    publishStatus: dto.publishStatus,
    resources: dto.resources.map(resource => ({
      id: resource.id,
      name: resource.name,
      url: resource.url,
      context: resource.context,
    })),
  };
}
