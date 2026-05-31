import { LanguageCode } from '../../../core/i18n/i18n.model';

export type NotePublishStatus = 'Draft' | 'Published';
export type NoteReactionKind = 'heart' | 'fire' | 'thinking' | 'neutral' | 'poop';
export type NoteViewSourceCategory =
  | 'Direct'
  | 'Internal'
  | 'Search'
  | 'Social'
  | 'External'
  | 'Unknown';

export interface NoteReactionCountsDto {
  heart: number;
  fire: number;
  thinking: number;
  neutral: number;
  poop: number;
}

export interface NoteTranslationDto {
  title: string;
  content: string;
  folder: string;
}

export interface NoteTranslationsDto {
  ru: NoteTranslationDto;
  en: NoteTranslationDto;
}

export interface NoteTagTranslationDto {
  name: string;
}

export interface NoteTagTranslationsDto {
  ru: NoteTagTranslationDto;
  en: NoteTagTranslationDto;
}

export interface NoteTagDto {
  id: number;
  name: string;
  slug: string;
  deletedAt: string | null;
  translations: NoteTagTranslationsDto;
}

export interface NoteSummaryDto {
  id: string;
  title: string;
  slug: string;
  folder: string;
  authorUsername: string;
  publishedAt: string | null;
  publishStatus: NotePublishStatus;
  updatedAt: string;
  excerpt: string;
  viewCount: number;
  tags: NoteTagDto[];
}

export interface NoteDetailDto extends NoteSummaryDto {
  content: string;
  createdAt: string;
  reactionCounts: NoteReactionCountsDto;
  translations: NoteTranslationsDto;
}

export interface NoteListDto {
  totalCount: number;
  totalPages: number;
  notes: NoteSummaryDto[];
}

export interface NoteTreeItemDto {
  title: string;
  slug: string;
  publishStatus: NotePublishStatus;
  publishedAt: string | null;
  updatedAt: string;
}

export interface NoteTreeFolderDto {
  folder: string;
  notes: NoteTreeItemDto[];
}

export interface NoteTreeDto {
  folders: NoteTreeFolderDto[];
}

export interface TagsDto {
  tags: NoteTagDto[];
}

export interface NoteStatsTotalsDto {
  viewCount: number;
  engagedViewCount: number;
  reactionCount: number;
}

export interface NoteStatsNoteDto {
  noteId: string;
  title: string;
  slug: string;
  viewCount: number;
  engagedViewCount: number;
  reactionCounts: NoteReactionCountsDto;
}

export interface NoteStatsDailyDto {
  noteId: string;
  title: string;
  slug: string;
  date: string;
  sourceCategory: NoteViewSourceCategory;
  viewCount: number;
  engagedViewCount: number;
}

export interface NoteStatsDto {
  dateFrom: string;
  dateTo: string;
  totals: NoteStatsTotalsDto;
  notes: NoteStatsNoteDto[];
  daily: NoteStatsDailyDto[];
}

export interface NoteTag {
  id: number;
  name: string;
  slug: string;
  deletedAt: string | null;
  translations: NoteTagTranslations;
}

export interface NoteReactionCounts {
  heart: number;
  fire: number;
  thinking: number;
  neutral: number;
  poop: number;
}

export interface NoteSummary {
  id: string;
  title: string;
  slug: string;
  folder: string;
  authorUsername: string;
  publishedAt: string | null;
  publishStatus: NotePublishStatus;
  updatedAt: string;
  excerpt: string;
  viewCount: number;
  tags: NoteTag[];
}

export interface NoteDetail extends NoteSummary {
  content: string;
  createdAt: string;
  reactionCounts: NoteReactionCounts;
  translations: NoteTranslations;
}

export interface NoteList {
  totalCount: number;
  totalPages: number;
  notes: NoteSummary[];
}

export interface NoteTreeItem {
  title: string;
  slug: string;
  publishStatus: NotePublishStatus;
  publishedAt: string | null;
  updatedAt: string;
}

export interface NoteTreeFolder {
  folder: string;
  notes: NoteTreeItem[];
}

export interface NoteTree {
  folders: NoteTreeFolder[];
}

export interface NoteTranslation {
  title: string;
  content: string;
  folder: string;
}

export interface NoteTranslations {
  ru: NoteTranslation;
  en: NoteTranslation;
}

export interface NoteTagTranslation {
  name: string;
}

export interface NoteTagTranslations {
  ru: NoteTagTranslation;
  en: NoteTagTranslation;
}

export interface NotePayload {
  slug: string;
  publishStatus: NotePublishStatus;
  tagIds: number[];
  translations: NoteTranslations;
}

export interface TagPayload {
  slug: string;
  translations: NoteTagTranslations;
}

export interface NoteReactionPayload {
  reactionKind: NoteReactionKind | null;
  clientToken: string;
}

export interface NoteStatsParams {
  dateFrom: string;
  dateTo: string;
  language: LanguageCode;
}

export interface NoteStatsTotals {
  viewCount: number;
  engagedViewCount: number;
  reactionCount: number;
}

export interface NoteStatsNote {
  noteId: string;
  title: string;
  slug: string;
  viewCount: number;
  engagedViewCount: number;
  reactionCounts: NoteReactionCounts;
}

export interface NoteStatsDaily {
  noteId: string;
  title: string;
  slug: string;
  date: string;
  sourceCategory: NoteViewSourceCategory;
  viewCount: number;
  engagedViewCount: number;
}

export interface NoteStats {
  dateFrom: string;
  dateTo: string;
  totals: NoteStatsTotals;
  notes: NoteStatsNote[];
  daily: NoteStatsDaily[];
}

export interface NoteListParams {
  page: number;
  pageSize: number;
  language: LanguageCode;
  onlyPublished: boolean;
  tagSlug: string | null;
  publishedFrom: string | null;
  publishedTo: string | null;
  searchQuery: string | null;
}

export function mapTagDto(dto: NoteTagDto): NoteTag {
  return {
    id: dto.id,
    name: dto.name,
    slug: dto.slug,
    deletedAt: dto.deletedAt,
    translations: dto.translations,
  };
}

export function mapNoteSummaryDto(dto: NoteSummaryDto): NoteSummary {
  return {
    id: dto.id,
    title: dto.title,
    slug: dto.slug,
    folder: dto.folder,
    authorUsername: dto.authorUsername,
    publishedAt: dto.publishedAt,
    publishStatus: dto.publishStatus,
    updatedAt: dto.updatedAt,
    excerpt: dto.excerpt,
    viewCount: dto.viewCount,
    tags: dto.tags.map(mapTagDto),
  };
}

export function mapNoteDetailDto(dto: NoteDetailDto): NoteDetail {
  return {
    ...mapNoteSummaryDto(dto),
    content: dto.content,
    createdAt: dto.createdAt,
    reactionCounts: mapReactionCountsDto(dto.reactionCounts),
    translations: dto.translations,
  };
}

export function mapNoteListDto(dto: NoteListDto): NoteList {
  return {
    totalCount: dto.totalCount,
    totalPages: dto.totalPages,
    notes: dto.notes.map(mapNoteSummaryDto),
  };
}

export function mapNoteTreeDto(dto: NoteTreeDto): NoteTree {
  return {
    folders: dto.folders.map((folder) => ({
      folder: folder.folder,
      notes: folder.notes.map((note) => ({ ...note })),
    })),
  };
}

export function mapReactionCountsDto(dto: NoteReactionCountsDto): NoteReactionCounts {
  return {
    heart: dto.heart,
    fire: dto.fire,
    thinking: dto.thinking,
    neutral: dto.neutral,
    poop: dto.poop,
  };
}

export function mapNoteStatsDto(dto: NoteStatsDto): NoteStats {
  return {
    dateFrom: dto.dateFrom,
    dateTo: dto.dateTo,
    totals: { ...dto.totals },
    notes: dto.notes.map((note) => ({
      noteId: note.noteId,
      title: note.title,
      slug: note.slug,
      viewCount: note.viewCount,
      engagedViewCount: note.engagedViewCount,
      reactionCounts: mapReactionCountsDto(note.reactionCounts),
    })),
    daily: dto.daily.map((item) => ({ ...item })),
  };
}
