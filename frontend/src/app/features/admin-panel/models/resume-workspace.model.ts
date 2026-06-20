export type ResumeCurrentStatus = 'notSet' | 'current' | 'notCurrent';

export interface ResumeProfileDto {
  fullName: string;
  roleRu: string;
  roleEn: string;
  locationRu: string;
  locationEn: string;
  email: string;
  phone: string;
  websiteUrl: string;
  linkedinUrl: string;
  githubUrl: string;
  telegram: string;
}

export interface ResumeSummaryDto {
  textRu: string;
  textEn: string;
}

export interface ResumeSkillGroupDto {
  categoryRu: string;
  categoryEn: string;
  items: string[];
}

export interface ResumeExperienceItemDto {
  companyRu: string;
  companyEn: string;
  positionRu: string;
  positionEn: string;
  locationRu: string;
  locationEn: string;
  startDate: string | null;
  endDate: string | null;
  currentStatus: ResumeCurrentStatus;
  summaryRu: string;
  summaryEn: string;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  projects: ResumeProjectItemDto[];
}

export interface ResumeProjectItemDto {
  nameRu: string;
  nameEn: string;
  roleRu: string;
  roleEn: string;
  descriptionRu: string;
  descriptionEn: string;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  url: string;
}

export interface ResumeEducationItemDto {
  institutionRu: string;
  institutionEn: string;
  degreeRu: string;
  degreeEn: string;
  fieldRu: string;
  fieldEn: string;
  locationRu: string;
  locationEn: string;
  startDate: string | null;
  endDate: string | null;
  descriptionRu: string;
  descriptionEn: string;
}

export interface ResumeLanguageItemDto {
  nameRu: string;
  nameEn: string;
  proficiencyRu: string;
  proficiencyEn: string;
}

export interface ResumeCertificationItemDto {
  nameRu: string;
  nameEn: string;
  issuerRu: string;
  issuerEn: string;
  issuedOn: string | null;
  expiresOn: string | null;
  credentialUrl: string;
}

export interface ResumeAdditionalSectionItemDto {
  titleRu: string;
  titleEn: string;
  descriptionRu: string;
  descriptionEn: string;
  url: string;
}

export interface ResumeAdditionalSectionDto {
  titleRu: string;
  titleEn: string;
  items: ResumeAdditionalSectionItemDto[];
}

export interface ResumeContentDto {
  profile: ResumeProfileDto;
  summary: ResumeSummaryDto;
  skills: ResumeSkillGroupDto[];
  experience: ResumeExperienceItemDto[];
  education: ResumeEducationItemDto[];
  languages: ResumeLanguageItemDto[];
  certifications: ResumeCertificationItemDto[];
  additionalSections: ResumeAdditionalSectionDto[];
}

export interface ResumeDto {
  id: number;
  title: string;
  content: ResumeContentDto;
  createdAt: string;
  updatedAt: string;
}

export interface ResumesDto {
  totalCount: number;
  totalPages: number;
  resumes: ResumeDto[];
}

export interface ResumePayloadDto {
  title: string;
  content: ResumeContentDto;
}

export interface ResumeProfile {
  fullName: string;
  roleRu: string;
  roleEn: string;
  locationRu: string;
  locationEn: string;
  email: string;
  phone: string;
  websiteUrl: string;
  linkedinUrl: string;
  githubUrl: string;
  telegram: string;
}

export interface ResumeSummary {
  textRu: string;
  textEn: string;
}

export interface ResumeSkillGroup {
  categoryRu: string;
  categoryEn: string;
  items: string[];
}

export interface ResumeExperienceItem {
  companyRu: string;
  companyEn: string;
  positionRu: string;
  positionEn: string;
  locationRu: string;
  locationEn: string;
  startDate: string | null;
  endDate: string | null;
  currentStatus: ResumeCurrentStatus;
  summaryRu: string;
  summaryEn: string;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  projects: ResumeProjectItem[];
}

export interface ResumeProjectItem {
  nameRu: string;
  nameEn: string;
  roleRu: string;
  roleEn: string;
  descriptionRu: string;
  descriptionEn: string;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  url: string;
}

export interface ResumeEducationItem {
  institutionRu: string;
  institutionEn: string;
  degreeRu: string;
  degreeEn: string;
  fieldRu: string;
  fieldEn: string;
  locationRu: string;
  locationEn: string;
  startDate: string | null;
  endDate: string | null;
  descriptionRu: string;
  descriptionEn: string;
}

export interface ResumeLanguageItem {
  nameRu: string;
  nameEn: string;
  proficiencyRu: string;
  proficiencyEn: string;
}

export interface ResumeCertificationItem {
  nameRu: string;
  nameEn: string;
  issuerRu: string;
  issuerEn: string;
  issuedOn: string | null;
  expiresOn: string | null;
  credentialUrl: string;
}

export interface ResumeAdditionalSectionItem {
  titleRu: string;
  titleEn: string;
  descriptionRu: string;
  descriptionEn: string;
  url: string;
}

export interface ResumeAdditionalSection {
  titleRu: string;
  titleEn: string;
  items: ResumeAdditionalSectionItem[];
}

export interface ResumeContent {
  profile: ResumeProfile;
  summary: ResumeSummary;
  skills: ResumeSkillGroup[];
  experience: ResumeExperienceItem[];
  education: ResumeEducationItem[];
  languages: ResumeLanguageItem[];
  certifications: ResumeCertificationItem[];
  additionalSections: ResumeAdditionalSection[];
}

export interface Resume {
  id: number;
  title: string;
  content: ResumeContent;
  createdAt: string;
  updatedAt: string;
}

export interface Resumes {
  totalCount: number;
  totalPages: number;
  resumes: Resume[];
}

export interface ResumePayload {
  title: string;
  content: ResumeContent;
}

export interface ResumeListParams {
  page: number;
  pageSize: number;
}

export function mapResumeDto(dto: ResumeDto): Resume {
  return {
    id: dto.id,
    title: dto.title,
    content: mapResumeContentDto(dto.content),
    createdAt: dto.createdAt,
    updatedAt: dto.updatedAt,
  };
}

export function mapResumesDto(dto: ResumesDto): Resumes {
  return {
    totalCount: dto.totalCount,
    totalPages: dto.totalPages,
    resumes: dto.resumes.map(mapResumeDto),
  };
}

export function toResumePayloadDto(payload: ResumePayload): ResumePayloadDto {
  return {
    title: payload.title,
    content: mapResumeContentToDto(payload.content),
  };
}

export function mapResumeContentDto(dto: ResumeContentDto): ResumeContent {
  return {
    profile: { ...dto.profile },
    summary: { ...dto.summary },
    skills: dto.skills.map((skill) => ({
      categoryRu: skill.categoryRu,
      categoryEn: skill.categoryEn,
      items: [...skill.items],
    })),
    experience: dto.experience.map((item) => ({
      companyRu: item.companyRu,
      companyEn: item.companyEn,
      positionRu: item.positionRu,
      positionEn: item.positionEn,
      locationRu: item.locationRu,
      locationEn: item.locationEn,
      startDate: item.startDate,
      endDate: item.endDate,
      currentStatus: item.currentStatus,
      summaryRu: item.summaryRu,
      summaryEn: item.summaryEn,
      highlightsRu: [...item.highlightsRu],
      highlightsEn: [...item.highlightsEn],
      technologies: [...item.technologies],
      projects: item.projects.map(mapResumeProjectItemDto),
    })),
    education: dto.education.map((item) => ({ ...item })),
    languages: dto.languages.map((item) => ({ ...item })),
    certifications: dto.certifications.map((item) => ({ ...item })),
    additionalSections: dto.additionalSections.map((section) => ({
      titleRu: section.titleRu,
      titleEn: section.titleEn,
      items: section.items.map((item) => ({ ...item })),
    })),
  };
}

function mapResumeContentToDto(content: ResumeContent): ResumeContentDto {
  return {
    profile: { ...content.profile },
    summary: { ...content.summary },
    skills: content.skills.map((skill) => ({
      categoryRu: skill.categoryRu,
      categoryEn: skill.categoryEn,
      items: [...skill.items],
    })),
    experience: content.experience.map((item) => ({
      companyRu: item.companyRu,
      companyEn: item.companyEn,
      positionRu: item.positionRu,
      positionEn: item.positionEn,
      locationRu: item.locationRu,
      locationEn: item.locationEn,
      startDate: item.startDate,
      endDate: item.endDate,
      currentStatus: item.currentStatus,
      summaryRu: item.summaryRu,
      summaryEn: item.summaryEn,
      highlightsRu: [...item.highlightsRu],
      highlightsEn: [...item.highlightsEn],
      technologies: [...item.technologies],
      projects: item.projects.map(mapResumeProjectItemToDto),
    })),
    education: content.education.map((item) => ({ ...item })),
    languages: content.languages.map((item) => ({ ...item })),
    certifications: content.certifications.map((item) => ({ ...item })),
    additionalSections: content.additionalSections.map((section) => ({
      titleRu: section.titleRu,
      titleEn: section.titleEn,
      items: section.items.map((item) => ({ ...item })),
    })),
  };
}

function mapResumeProjectItemDto(item: ResumeProjectItemDto): ResumeProjectItem {
  return {
    nameRu: item.nameRu,
    nameEn: item.nameEn,
    roleRu: item.roleRu,
    roleEn: item.roleEn,
    descriptionRu: item.descriptionRu,
    descriptionEn: item.descriptionEn,
    highlightsRu: [...item.highlightsRu],
    highlightsEn: [...item.highlightsEn],
    technologies: [...item.technologies],
    url: item.url,
  };
}

function mapResumeProjectItemToDto(item: ResumeProjectItem): ResumeProjectItemDto {
  return {
    nameRu: item.nameRu,
    nameEn: item.nameEn,
    roleRu: item.roleRu,
    roleEn: item.roleEn,
    descriptionRu: item.descriptionRu,
    descriptionEn: item.descriptionEn,
    highlightsRu: [...item.highlightsRu],
    highlightsEn: [...item.highlightsEn],
    technologies: [...item.technologies],
    url: item.url,
  };
}
