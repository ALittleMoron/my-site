import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { MatrixQuestionQueueService } from './matrix-question-queue.service';

describe('MatrixQuestionQueueService', () => {
  let service: MatrixQuestionQueueService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        MatrixQuestionQueueService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(MatrixQuestionQueueService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads queued questions in backend order', () => {
    let firstQuestion: string | undefined;

    service.listQueuedQuestions().subscribe((questions) => {
      firstQuestion = questions[0].question;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/queued-questions'),
    );
    expect(req.request.method).toBe('GET');
    req.flush({
      questions: [
        {
          id: 1,
          question: 'What is PEP 8?',
          grade: null,
          sheet: null,
          section: null,
          subsection: null,
          suggestedByUsername: null,
          createdAt: '2026-06-07T12:00:00+00:00',
        },
      ],
    });

    expect(firstQuestion).toBe('What is PEP 8?');
  });

  it('rejects queued question', () => {
    let completed = false;

    service.rejectQueuedQuestion(7).subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/queued-questions/7'),
    );
    expect(req.request.method).toBe('DELETE');
    req.flush(null, { status: 204, statusText: 'No Content' });

    expect(completed).toBe(true);
  });

  it('creates queued question manually', () => {
    let createdQuestion: string | undefined;

    service.createQueuedQuestion('What is PEP 8?').subscribe((question) => {
      createdQuestion = question.question;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/queued-questions'),
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ question: 'What is PEP 8?' });
    req.flush({
      id: 7,
      question: 'What is PEP 8?',
      grade: null,
      sheet: null,
      section: null,
      subsection: null,
      suggestedByUsername: null,
      createdAt: '2026-06-07T12:00:00+00:00',
    });

    expect(createdQuestion).toBe('What is PEP 8?');
  });

  it('imports queued questions from file upload form data', () => {
    let importedQuestions: string[] | undefined;
    const file = new File(['What is PEP 8?'], 'questions.txt', { type: 'text/plain' });

    service.importQueuedQuestions(file).subscribe((questions) => {
      importedQuestions = questions.map((question) => question.question);
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/queued-questions/import'),
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toBeInstanceOf(FormData);
    expect((req.request.body as FormData).get('file')).toBe(file);
    req.flush({
      questions: [
        {
          id: 7,
          question: 'What is PEP 8?',
          grade: null,
          sheet: null,
          section: null,
          subsection: null,
          suggestedByUsername: null,
          createdAt: '2026-06-07T12:00:00+00:00',
        },
        {
          id: 8,
          question: 'What is Black?',
          grade: null,
          sheet: null,
          section: null,
          subsection: null,
          suggestedByUsername: null,
          createdAt: '2026-06-07T12:01:00+00:00',
        },
      ],
    });

    expect(importedQuestions).toEqual(['What is PEP 8?', 'What is Black?']);
  });

  it('creates matrix question from queued question', () => {
    let createdId: string | undefined;

    service
      .createQuestionFromQueue(
        7,
        {
          slug: 'pep-8',
          subsectionId: 3,
          grade: 'Junior',
          publishStatus: 'Draft',
          translations: {
            ru: {
              question: 'Что такое PEP 8?',
              answer: 'Ответ',
              interviewExpectedAnswer: 'Ожидаемый ответ',
            },
            en: {
              question: 'What is PEP 8?',
              answer: 'Answer',
              interviewExpectedAnswer: 'Expected answer',
            },
          },
          resources: [],
        },
        'en',
      )
      .subscribe((created) => {
        createdId = created.id;
      });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/admin/competency-matrix/queued-questions/7/create-item'),
    );
    expect(req.request.method).toBe('POST');
    expect(req.request.params.get('language')).toBe('en');
    expect(req.request.body.slug).toBe('pep-8');
    expect(req.request.body.subsectionId).toBe(3);
    expect(req.request.body.sheetKey).toBeUndefined();
    expect(req.request.body.translations.en.section).toBeUndefined();
    req.flush({ id: '10', slug: 'pep-8', question: 'What is PEP 8?' });

    expect(createdId).toBe('10');
  });
});
