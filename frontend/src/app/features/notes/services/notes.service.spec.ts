import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { NotesService } from './notes.service';

describe('NotesService', () => {
  let service: NotesService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [NotesService, ApiClient, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(NotesService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads notes with pagination, visibility, and tag filters', () => {
    let firstTitle: string | undefined;

    service
      .getNotes({ page: 2, pageSize: 10, onlyPublished: false, tagSlug: 'python' })
      .subscribe((list) => {
        firstTitle = list.notes[0].title;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('2');
    expect(req.request.params.get('pageSize')).toBe('10');
    expect(req.request.params.get('onlyPublished')).toBe('false');
    expect(req.request.params.get('tagSlug')).toBe('python');
    req.flush({
      totalCount: 1,
      totalPages: 1,
      notes: [
        {
          id: '00000000-0000-0000-0000-000000000001',
          title: 'Typed notes',
          content: 'Ignored in list',
          slug: 'typed-notes',
          folder: 'Engineering',
          authorUsername: 'admin',
          publishedAt: '2026-01-02T03:04:05+00:00',
          publishStatus: 'Published',
          updatedAt: '2026-01-03T03:04:05+00:00',
          excerpt: 'Excerpt',
          tags: [{ id: 1, name: 'Python', slug: 'python', deletedAt: null }],
        },
      ],
    });

    expect(firstTitle).toBe('Typed notes');
  });

  it('loads detail with explicit visibility', () => {
    let content: string | undefined;

    service.getNote('typed-notes', true).subscribe((note) => {
      content = note.content;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/detail/typed-notes'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('onlyPublished')).toBe('true');
    req.flush({
      id: '00000000-0000-0000-0000-000000000001',
      title: 'Typed notes',
      content: '# Markdown',
      slug: 'typed-notes',
      folder: 'Engineering',
      authorUsername: 'admin',
      publishedAt: '2026-01-02T03:04:05+00:00',
      publishStatus: 'Published',
      createdAt: '2026-01-01T03:04:05+00:00',
      updatedAt: '2026-01-03T03:04:05+00:00',
      excerpt: 'Markdown',
      tags: [],
    });

    expect(content).toBe('# Markdown');
  });

  it('loads tree without tag filters', () => {
    let firstFolder: string | undefined;

    service.getTree().subscribe((tree) => {
      firstFolder = tree.folders[0].folder;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tree'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.keys()).toEqual([]);
    req.flush({
      folders: [
        {
          folder: 'Engineering',
          notes: [
            {
              title: 'Typed notes',
              slug: 'typed-notes',
              publishStatus: 'Published',
              publishedAt: '2026-01-02T03:04:05+00:00',
              updatedAt: '2026-01-03T03:04:05+00:00',
            },
          ],
        },
      ],
    });

    expect(firstFolder).toBe('Engineering');
  });

  it('creates and updates notes with editable slug and tags', () => {
    service
      .createNote({
        title: 'New note',
        content: 'Content',
        slug: 'new-note',
        folder: 'Inbox',
        publishStatus: 'Draft',
        tagIds: [1],
      })
      .subscribe();

    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.body.slug).toBe('new-note');
    expect(createReq.request.body.tagIds).toEqual([1]);
    createReq.flush(noteDetailDto());

    service
      .updateNote('old-note', {
        title: 'New note',
        content: 'Content',
        slug: 'new-note',
        folder: 'Inbox',
        publishStatus: 'Published',
        tagIds: [1, 2],
      })
      .subscribe();

    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/detail/old-note'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.body.publishStatus).toBe('Published');
    expect(updateReq.request.body.tagIds).toEqual([1, 2]);
    updateReq.flush(noteDetailDto());
  });

  it('calls note publish endpoints', () => {
    service.publishNote('draft-note').subscribe();
    const publishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/draft-note/set-published'),
    );
    expect(publishReq.request.method).toBe('POST');
    publishReq.flush(null);

    service.unpublishNote('published-note').subscribe();
    const unpublishReq = httpMock.expectOne((r) =>
      r.url.endsWith('/api/notes/detail/published-note/set-draft'),
    );
    expect(unpublishReq.request.method).toBe('POST');
    unpublishReq.flush(null);
  });

  it('manages tags', () => {
    service.getTags(true).subscribe();
    const listReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags'));
    expect(listReq.request.params.get('includeDeleted')).toBe('true');
    listReq.flush({ tags: [] });

    service.createTag({ name: 'Backend', slug: 'backend' }).subscribe();
    const createReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.body).toEqual({ name: 'Backend', slug: 'backend' });
    createReq.flush({ id: 1, name: 'Backend', slug: 'backend', deletedAt: null });

    service.updateTag(1, { name: 'Architecture', slug: 'architecture' }).subscribe();
    const updateReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1'));
    expect(updateReq.request.method).toBe('PUT');
    updateReq.flush({ id: 1, name: 'Architecture', slug: 'architecture', deletedAt: null });

    service.deleteTag(1).subscribe();
    const deleteReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1'));
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);

    service.restoreTag(1).subscribe();
    const restoreReq = httpMock.expectOne((r) => r.url.endsWith('/api/notes/tags/1/restore'));
    expect(restoreReq.request.method).toBe('POST');
    restoreReq.flush(null);
  });
});

function noteDetailDto(): unknown {
  return {
    id: '00000000-0000-0000-0000-000000000001',
    title: 'New note',
    content: 'Content',
    slug: 'new-note',
    folder: 'Inbox',
    authorUsername: 'admin',
    publishedAt: null,
    publishStatus: 'Draft',
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-03T03:04:05+00:00',
    excerpt: 'Content',
    tags: [],
  };
}
