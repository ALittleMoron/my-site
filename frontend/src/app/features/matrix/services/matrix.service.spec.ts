import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MatrixService } from './matrix.service';
import { ApiClient } from '../../../core/http/api-client.service';

describe('MatrixService', () => {
  let service: MatrixService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [MatrixService, ApiClient, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(MatrixService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads localized sheets from the backend matrix endpoint', () => {
    let result: { key: string; name: string }[] | undefined;

    service.getSheets('en').subscribe((sheets) => {
      result = sheets;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/sheets'));
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({ sheets: [{ key: 'python', name: 'Python' }] });

    expect(result).toEqual([{ key: 'python', name: 'Python' }]);
  });

  it('loads grouped questions with sheet key, publication, and language filters', () => {
    let resultSheet: string | undefined;
    let firstQuestion: string | undefined;
    let firstSlug: string | undefined;

    service.getQuestions('python', true, 'en').subscribe((list) => {
      resultSheet = list.sheet;
      firstQuestion = list.sections[0].subsections[0].grades[0].questions[0].question;
      firstSlug = list.sections[0].subsections[0].grades[0].questions[0].slug;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items'));
    expect(req.request.params.get('sheetKey')).toBe('python');
    expect(req.request.params.get('onlyPublished')).toBe('true');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({
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
                  items: [{ id: 1, slug: 'what-is-pep8', question: 'What is PEP8?' }],
                },
              ],
            },
          ],
        },
      ],
    });

    expect(resultSheet).toBe('Python');
    expect(firstQuestion).toBe('What is PEP8?');
    expect(firstSlug).toBe('what-is-pep8');
  });

  it('loads localized question detail from the backend detail endpoint', () => {
    let resultQuestion: string | undefined;
    let resultTranslation: string | undefined;
    let resultSlug: string | undefined;

    service.getQuestion(1, false, 'en').subscribe((question) => {
      resultQuestion = question.question;
      resultTranslation = question.translations.ru.question;
      resultSlug = question.slug;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items/detail/1'));
    expect(req.request.params.get('onlyPublished')).toBe('false');
    expect(req.request.params.get('language')).toBe('en');
    req.flush(matrixDetailDto());

    expect(resultQuestion).toBe('What is PEP8?');
    expect(resultTranslation).toBe('Что такое PEP8?');
    expect(resultSlug).toBe('what-is-pep8');
  });

  it('loads public localized question detail by slug', () => {
    let resultSlug: string | undefined;

    service.getPublicQuestion('how-to-write-function', 'ru').subscribe((question) => {
      resultSlug = question.slug;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/competency-matrix/items/public/how-to-write-function'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('language')).toBe('ru');
    expect(req.request.params.has('onlyPublished')).toBe(false);
    req.flush(matrixDetailDto({ slug: 'how-to-write-function' }));

    expect(resultSlug).toBe('how-to-write-function');
  });

  it('searchResources loads localized resource matches with limit and language', () => {
    let firstResourceName: string | undefined;
    let firstTranslation: string | undefined;

    service.searchResources('python', 5, 'en').subscribe((resources) => {
      firstResourceName = resources[0].name;
      firstTranslation = resources[0].translations.ru.name;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/competency-matrix/resources/search'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('searchName')).toBe('python');
    expect(req.request.params.get('limit')).toBe('5');
    expect(req.request.params.get('language')).toBe('en');
    req.flush({
      resources: [
        {
          id: 1,
          name: 'Python docs',
          url: 'https://docs.python.org',
          translations: { ru: { name: 'Документация Python' }, en: { name: 'Python docs' } },
        },
      ],
    });

    expect(firstResourceName).toBe('Python docs');
    expect(firstTranslation).toBe('Документация Python');
  });

  it('createQuestion posts localized payload and maps saved detail', () => {
    let resultId: number | undefined;

    service.createQuestion(matrixPayload(), 'en').subscribe((question) => {
      resultId = question.id;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items'));
    expect(req.request.method).toBe('POST');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.body.slug).toBe('what-is-pep8');
    expect(req.request.body.resources).toEqual([
      {
        resourceId: 1,
        translations: {
          ru: { context: 'Читать сначала' },
          en: { context: 'Read first' },
        },
      },
    ]);
    req.flush(matrixDetailDto({ id: 7 }));

    expect(resultId).toBe(7);
  });

  it('updateQuestion puts localized payload to detail endpoint and maps saved detail', () => {
    let resultQuestion: string | undefined;

    service.updateQuestion(7, matrixPayload(), 'ru').subscribe((question) => {
      resultQuestion = question.question;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items/detail/7'));
    expect(req.request.method).toBe('PUT');
    expect(req.request.params.get('language')).toBe('ru');
    expect(req.request.body.slug).toBe('what-is-pep8');
    expect(req.request.body.sheetKey).toBe('python');
    req.flush(matrixDetailDto({ question: 'Что такое PEP8?' }));

    expect(resultQuestion).toBe('Что такое PEP8?');
  });

  it('publishQuestion posts to set-published endpoint', () => {
    let completed = false;

    service.publishQuestion(42).subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/competency-matrix/items/detail/42/set-published'),
    );
    expect(req.request.method).toBe('POST');
    req.flush(null);

    expect(completed).toBe(true);
  });

  it('unpublishQuestion posts to set-draft endpoint', () => {
    let completed = false;

    service.unpublishQuestion(7).subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/competency-matrix/items/detail/7/set-draft'),
    );
    expect(req.request.method).toBe('POST');
    req.flush(null);

    expect(completed).toBe(true);
  });

  it('deleteQuestion sends DELETE to detail endpoint', () => {
    let completed = false;

    service.deleteQuestion(99).subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items/detail/99'));
    expect(req.request.method).toBe('DELETE');
    req.flush(null);

    expect(completed).toBe(true);
  });
});

function matrixPayload() {
  return {
    slug: 'what-is-pep8',
    sheetKey: 'python',
    grade: 'Junior',
    publishStatus: 'Draft',
    translations: {
      ru: {
        question: 'Что такое PEP8?',
        answer: 'Ответ',
        interviewExpectedAnswer: 'Ожидаемый ответ',
        sheet: 'Питон',
        section: 'Основы',
        subsection: 'Стиль',
      },
      en: {
        question: 'What is PEP8?',
        answer: 'Answer',
        interviewExpectedAnswer: 'Expected answer',
        sheet: 'Python',
        section: 'Core',
        subsection: 'Style',
      },
    },
    resources: [
      {
        resourceId: 1,
        translations: {
          ru: { context: 'Читать сначала' },
          en: { context: 'Read first' },
        },
      },
    ],
  } as const;
}

function matrixDetailDto(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: 1,
    slug: 'what-is-pep8',
    question: 'What is PEP8?',
    answer: 'Answer',
    interviewExpectedAnswer: 'Expected answer',
    sheetKey: 'python',
    sheet: 'Python',
    grade: 'Junior',
    section: 'Core',
    subsection: 'Style',
    publishStatus: 'Published',
    translations: {
      ru: {
        question: 'Что такое PEP8?',
        answer: 'Ответ',
        interviewExpectedAnswer: 'Ожидаемый ответ',
        sheet: 'Питон',
        section: 'Основы',
        subsection: 'Стиль',
      },
      en: {
        question: 'What is PEP8?',
        answer: 'Answer',
        interviewExpectedAnswer: 'Expected answer',
        sheet: 'Python',
        section: 'Core',
        subsection: 'Style',
      },
    },
    resources: [
      {
        id: 1,
        name: 'Python docs',
        url: 'https://docs.python.org',
        context: 'Read first',
        translations: {
          ru: { name: 'Документация Python', context: 'Читать сначала' },
          en: { name: 'Python docs', context: 'Read first' },
        },
      },
    ],
    ...overrides,
  };
}
