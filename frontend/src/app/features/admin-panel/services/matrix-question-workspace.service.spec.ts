import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { MatrixQuestionWorkspaceService } from './matrix-question-workspace.service';

describe('MatrixQuestionWorkspaceService', () => {
  let service: MatrixQuestionWorkspaceService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        MatrixQuestionWorkspaceService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(MatrixQuestionWorkspaceService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('serializes workspace filters with repeated array query params', () => {
    let total = 0;

    service
      .listWorkspaceItems({
        page: 2,
        pageSize: 50,
        language: 'en',
        sort: 'dangerousPublished',
        searchQuery: 'typing',
        sheetKeys: ['python', 'sql'],
        grades: ['Junior', 'Senior'],
        sections: ['Core'],
        subsections: ['Syntax'],
        publishStatuses: ['Draft', 'Published'],
        publishedFrom: '2026-01-01',
        publishedTo: '2026-02-01',
        hasMissingFields: true,
      })
      .subscribe((workspace) => {
        total = workspace.summary.total;
      });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/items/workspace'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('page')).toBe('2');
    expect(req.request.params.get('pageSize')).toBe('50');
    expect(req.request.params.getAll('sheetKeys')).toEqual(['python', 'sql']);
    expect(req.request.params.getAll('grades')).toEqual(['Junior', 'Senior']);
    expect(req.request.params.get('hasMissingFields')).toBe('true');
    req.flush({
      totalCount: 1,
      totalPages: 1,
      summary: {
        total: 1,
        draft: 0,
        missingDraft: 0,
        dangerousPublished: 1,
        readyPublished: 0,
      },
      items: [
        {
          id: 1,
          slug: 'typing',
          question: 'What is typing?',
          sheetKey: 'python',
          sheet: 'Python',
          grade: 'Junior',
          section: 'Core',
          subsection: 'Syntax',
          publishStatus: 'Published',
          publishedAt: '2026-01-01T00:00:00+00:00',
          missingFields: ['answerEn'],
        },
      ],
    });

    expect(total).toBe(1);
  });

  it('loads filter options from the admin endpoint', () => {
    let firstSubsection = '';

    service.getFilterOptions('ru').subscribe((options) => {
      firstSubsection = options.sheets[0].sections[0].subsections[0];
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/items/filter-options'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    req.flush({
      sheets: [
        {
          key: 'python',
          label: 'Питон',
          sections: [{ label: 'Основы', subsections: ['Синтаксис'] }],
        },
      ],
      grades: ['Junior'],
      sections: ['Основы'],
      subsections: ['Синтаксис'],
      publishStatuses: ['Draft', 'Published'],
    });

    expect(firstSubsection).toBe('Синтаксис');
  });

  it('searches resources through the admin endpoint', () => {
    let resourceName = '';

    service.searchResources('python', 10, 'en').subscribe((resources) => {
      resourceName = resources[0].translations.en.name;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/resources/search'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('searchName')).toBe('python');
    expect(req.request.params.get('limit')).toBe('10');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({
      resources: [
        {
          id: 1,
          name: 'Python docs',
          url: 'https://docs.python.org',
          translations: {
            ru: { name: 'Документация Python' },
            en: { name: 'Python docs' },
          },
        },
      ],
    });

    expect(resourceName).toBe('Python docs');
  });

  it('loads public preview data through public matrix endpoints', () => {
    let sheetCount = 0;
    let questionCount = 0;

    service.listPublicPreviewSheets('en').subscribe((sheets) => {
      sheetCount = sheets.length;
    });
    service.listPublicPreviewQuestions('python', 'en').subscribe((questions) => {
      questionCount = questions.sections[0].subsections[0].grades[0].questions.length;
    });

    const sheetsReq = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/sheets'));
    expect(sheetsReq.request.params.get('language')).toBe('en');
    sheetsReq.flush({ sheets: [{ key: 'python', name: 'Python' }] });

    const questionsReq = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items'));
    expect(questionsReq.request.params.get('sheetKey')).toBe('python');
    expect(questionsReq.request.params.get('language')).toBe('en');
    questionsReq.flush({
      sheetKey: 'python',
      sheet: 'Python',
      sections: [
        {
          section: 'Core',
          subsections: [
            {
              subsection: 'Syntax',
              grades: [
                {
                  grade: 'Junior',
                  items: [{ id: 1, slug: 'typing', question: 'What is typing?' }],
                },
              ],
            },
          ],
        },
      ],
    });

    expect(sheetCount).toBe(1);
    expect(questionCount).toBe(1);
  });
});
