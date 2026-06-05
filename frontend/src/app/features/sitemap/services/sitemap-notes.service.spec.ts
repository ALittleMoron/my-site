import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { SitemapNotesService } from './sitemap-notes.service';

describe('SitemapNotesService', () => {
  let api: { get: jest.Mock };
  let service: SitemapNotesService;

  beforeEach(() => {
    api = {
      get: jest.fn(),
    };

    TestBed.configureTestingModule({
      providers: [SitemapNotesService, { provide: ApiClient, useValue: api }],
    });
    service = TestBed.inject(SitemapNotesService);
  });

  it('fetches every page of published notes for the active sitemap language', () => {
    api.get
      .mockReturnValueOnce(
        of({
          totalPages: 2,
          notes: [note('typed-notes', 'Typed notes')],
        }),
      )
      .mockReturnValueOnce(
        of({
          totalPages: 2,
          notes: [note('angular-ssr', 'Angular SSR')],
        }),
      );

    let slugs: string[] = [];
    service.getPublishedNotes('en').subscribe((notes) => {
      slugs = notes.map((item) => item.slug);
    });

    expect(api.get).toHaveBeenNthCalledWith(1, '/api/notes', {
      page: '1',
      pageSize: '100',
      language: 'en',
      onlyPublished: 'true',
    });
    expect(api.get).toHaveBeenNthCalledWith(2, '/api/notes', {
      page: '2',
      pageSize: '100',
      language: 'en',
      onlyPublished: 'true',
    });
    expect(slugs).toEqual(['typed-notes', 'angular-ssr']);
  });
});

function note(slug: string, title: string): { slug: string; title: string } {
  return {
    title,
    slug,
  };
}
