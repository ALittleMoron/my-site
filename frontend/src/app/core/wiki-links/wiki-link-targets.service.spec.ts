import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../http/api-client.service';
import { WikiLinkTargetsService } from './wiki-link-targets.service';

describe('WikiLinkTargetsService', () => {
  let service: WikiLinkTargetsService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        WikiLinkTargetsService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(WikiLinkTargetsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads typed wiki-link targets with explicit language', () => {
    let noteTargets: ReadonlySet<string> | undefined;
    let matrixTargets: ReadonlySet<string> | undefined;

    service.getTargets('ru').subscribe((targets) => {
      noteTargets = targets.get('notes');
      matrixTargets = targets.get('matrix');
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/wiki-links/targets'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    req.flush({
      targets: [
        { type: 'notes', slugs: ['typed-notes'] },
        { type: 'matrix', slugs: ['how-to-write-function'] },
      ],
    });

    expect(noteTargets).toEqual(new Set(['typed-notes']));
    expect(matrixTargets).toEqual(new Set(['how-to-write-function']));
  });
});
