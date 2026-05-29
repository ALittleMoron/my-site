export type NotePublishStatus = 'Draft' | 'Published';

export interface NoteTagDto {
  id: number;
  name: string;
  slug: string;
  deletedAt: string | null;
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
  tags: NoteTagDto[];
}

export interface NoteDetailDto extends NoteSummaryDto {
  content: string;
  createdAt: string;
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

export interface NoteTag {
  id: number;
  name: string;
  slug: string;
  deletedAt: string | null;
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
  tags: NoteTag[];
}

export interface NoteDetail extends NoteSummary {
  content: string;
  createdAt: string;
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

export interface NotePayload {
  title: string;
  content: string;
  slug: string;
  folder: string;
  publishStatus: NotePublishStatus;
  tagIds: number[];
}

export interface TagPayload {
  name: string;
  slug: string;
}

export interface NoteListParams {
  page: number;
  pageSize: number;
  onlyPublished: boolean;
  tagSlug: string | null;
}

export function mapTagDto(dto: NoteTagDto): NoteTag {
  return {
    id: dto.id,
    name: dto.name,
    slug: dto.slug,
    deletedAt: dto.deletedAt,
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
    tags: dto.tags.map(mapTagDto),
  };
}

export function mapNoteDetailDto(dto: NoteDetailDto): NoteDetail {
  return {
    ...mapNoteSummaryDto(dto),
    content: dto.content,
    createdAt: dto.createdAt,
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
