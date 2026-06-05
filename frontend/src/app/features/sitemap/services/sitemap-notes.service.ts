import { Injectable, inject } from '@angular/core';
import { Observable, forkJoin, map, of, switchMap } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { LanguageCode } from '../../../core/i18n/i18n.model';

const SITEMAP_NOTES_PAGE_SIZE = 100;

export interface SitemapNote {
  title: string;
  slug: string;
}

interface SitemapNoteListDto {
  totalPages: number;
  notes: SitemapNote[];
}

@Injectable({ providedIn: 'root' })
export class SitemapNotesService {
  private readonly api = inject(ApiClient);

  getPublishedNotes(language: LanguageCode): Observable<SitemapNote[]> {
    return this.getPublishedNotesPage(1, language).pipe(
      switchMap((firstPage) => {
        if (firstPage.totalPages <= 1) {
          return of(firstPage.notes);
        }
        const followUpPages = Array.from({ length: firstPage.totalPages - 1 }, (_, index) =>
          this.getPublishedNotesPage(index + 2, language),
        );
        return forkJoin(followUpPages).pipe(
          map((pages) => [firstPage.notes, ...pages.map((page) => page.notes)].flat()),
        );
      }),
    );
  }

  private getPublishedNotesPage(
    page: number,
    language: LanguageCode,
  ): Observable<SitemapNoteListDto> {
    return this.api.get<SitemapNoteListDto>('/api/notes', {
      page: String(page),
      pageSize: String(SITEMAP_NOTES_PAGE_SIZE),
      language,
      onlyPublished: 'true',
    });
  }
}
