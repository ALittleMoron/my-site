export interface ResumeProfileDto {
  fullName: string | null;
  roleRu: string | null;
  roleEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  email: string | null;
  phone: string | null;
  websiteUrl: string | null;
  linkedinUrl: string | null;
  githubUrl: string | null;
  telegram: string | null;
}

export interface ResumeSummaryDto {
  textRu: string | null;
  textEn: string | null;
}

export interface ResumeSkillGroupDto {
  categoryRu: string | null;
  categoryEn: string | null;
  items: string[];
}

export interface ResumeExperienceItemDto {
  companyRu: string | null;
  companyEn: string | null;
  positionRu: string | null;
  positionEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  startDate: string | null;
  endDate: string | null;
  isCurrent: boolean | null;
  summaryRu: string | null;
  summaryEn: string | null;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
}

export interface ResumeProjectItemDto {
  nameRu: string | null;
  nameEn: string | null;
  roleRu: string | null;
  roleEn: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  url: string | null;
}

export interface ResumeEducationItemDto {
  institutionRu: string | null;
  institutionEn: string | null;
  degreeRu: string | null;
  degreeEn: string | null;
  fieldRu: string | null;
  fieldEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  startDate: string | null;
  endDate: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
}

export interface ResumeLanguageItemDto {
  nameRu: string | null;
  nameEn: string | null;
  proficiencyRu: string | null;
  proficiencyEn: string | null;
}

export interface ResumeCertificationItemDto {
  nameRu: string | null;
  nameEn: string | null;
  issuerRu: string | null;
  issuerEn: string | null;
  issuedOn: string | null;
  expiresOn: string | null;
  credentialUrl: string | null;
}

export interface ResumeAdditionalSectionItemDto {
  titleRu: string | null;
  titleEn: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
  url: string | null;
}

export interface ResumeAdditionalSectionDto {
  titleRu: string | null;
  titleEn: string | null;
  items: ResumeAdditionalSectionItemDto[];
}

export interface ResumeContentDto {
  profile: ResumeProfileDto;
  summary: ResumeSummaryDto;
  skills: ResumeSkillGroupDto[];
  experience: ResumeExperienceItemDto[];
  projects: ResumeProjectItemDto[];
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
  fullName: string | null;
  roleRu: string | null;
  roleEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  email: string | null;
  phone: string | null;
  websiteUrl: string | null;
  linkedinUrl: string | null;
  githubUrl: string | null;
  telegram: string | null;
}

export interface ResumeSummary {
  textRu: string | null;
  textEn: string | null;
}

export interface ResumeSkillGroup {
  categoryRu: string | null;
  categoryEn: string | null;
  items: string[];
}

export interface ResumeExperienceItem {
  companyRu: string | null;
  companyEn: string | null;
  positionRu: string | null;
  positionEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  startDate: string | null;
  endDate: string | null;
  isCurrent: boolean | null;
  summaryRu: string | null;
  summaryEn: string | null;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
}

export interface ResumeProjectItem {
  nameRu: string | null;
  nameEn: string | null;
  roleRu: string | null;
  roleEn: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
  highlightsRu: string[];
  highlightsEn: string[];
  technologies: string[];
  url: string | null;
}

export interface ResumeEducationItem {
  institutionRu: string | null;
  institutionEn: string | null;
  degreeRu: string | null;
  degreeEn: string | null;
  fieldRu: string | null;
  fieldEn: string | null;
  locationRu: string | null;
  locationEn: string | null;
  startDate: string | null;
  endDate: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
}

export interface ResumeLanguageItem {
  nameRu: string | null;
  nameEn: string | null;
  proficiencyRu: string | null;
  proficiencyEn: string | null;
}

export interface ResumeCertificationItem {
  nameRu: string | null;
  nameEn: string | null;
  issuerRu: string | null;
  issuerEn: string | null;
  issuedOn: string | null;
  expiresOn: string | null;
  credentialUrl: string | null;
}

export interface ResumeAdditionalSectionItem {
  titleRu: string | null;
  titleEn: string | null;
  descriptionRu: string | null;
  descriptionEn: string | null;
  url: string | null;
}

export interface ResumeAdditionalSection {
  titleRu: string | null;
  titleEn: string | null;
  items: ResumeAdditionalSectionItem[];
}

export interface ResumeContent {
  profile: ResumeProfile;
  summary: ResumeSummary;
  skills: ResumeSkillGroup[];
  experience: ResumeExperienceItem[];
  projects: ResumeProjectItem[];
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
      isCurrent: item.isCurrent,
      summaryRu: item.summaryRu,
      summaryEn: item.summaryEn,
      highlightsRu: [...item.highlightsRu],
      highlightsEn: [...item.highlightsEn],
      technologies: [...item.technologies],
    })),
    projects: dto.projects.map((item) => ({
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
      isCurrent: item.isCurrent,
      summaryRu: item.summaryRu,
      summaryEn: item.summaryEn,
      highlightsRu: [...item.highlightsRu],
      highlightsEn: [...item.highlightsEn],
      technologies: [...item.technologies],
    })),
    projects: content.projects.map((item) => ({
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
