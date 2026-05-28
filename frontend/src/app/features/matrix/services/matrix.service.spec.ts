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

  it('loads sheets from the backend matrix endpoint', () => {
    let result: string[] | undefined;

    service.getSheets().subscribe((sheets) => {
      result = sheets;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/sheets'));
    expect(req.request.method).toBe('GET');
    req.flush({ sheets: ['Python', 'SQL'] });

    expect(result).toEqual(['Python', 'SQL']);
  });

  it('loads grouped questions with sheet and publication filters', () => {
    let resultSheet: string | undefined;
    let firstQuestion: string | undefined;

    service.getQuestions('Python', true).subscribe((list) => {
      resultSheet = list.sheet;
      firstQuestion = list.sections[0].subsections[0].grades[0].questions[0].question;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items'));
    expect(req.request.params.get('sheetName')).toBe('Python');
    expect(req.request.params.get('onlyPublished')).toBe('true');
    req.flush({
      sheet: 'Python',
      sections: [
        {
          section: 'Core',
          subsections: [
            {
              subsection: 'Syntax',
              grades: [{ grade: 'Junior', items: [{ id: 1, question: 'What is PEP8?' }] }],
            },
          ],
        },
      ],
    });

    expect(resultSheet).toBe('Python');
    expect(firstQuestion).toBe('What is PEP8?');
  });

  it('loads question detail from the backend detail endpoint', () => {
    let resultQuestion: string | undefined;

    service.getQuestion(1, false).subscribe((question) => {
      resultQuestion = question.question;
    });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items/detail/1'));
    expect(req.request.params.get('onlyPublished')).toBe('false');
    req.flush({
      id: 1,
      question: 'What is PEP8?',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected answer',
      sheet: 'Python',
      grade: 'Junior',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Published',
      resources: [],
    });

    expect(resultQuestion).toBe('What is PEP8?');
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

  it('searchResources loads resource matches with limit', () => {
    let firstResourceName: string | undefined;

    service.searchResources('python', 5).subscribe((resources) => {
      firstResourceName = resources[0].name;
    });

    const req = httpMock.expectOne((r) =>
      r.url.endsWith('/api/competency-matrix/resources/search'),
    );
    expect(req.request.method).toBe('GET');
    expect(req.request.params.get('searchName')).toBe('python');
    expect(req.request.params.get('limit')).toBe('5');
    req.flush({
      resources: [{ id: 1, name: 'Python docs', url: 'https://docs.python.org' }],
    });

    expect(firstResourceName).toBe('Python docs');
  });

  it('createQuestion posts payload and maps saved detail', () => {
    let resultId: number | undefined;

    service
      .createQuestion({
        question: 'Question',
        answer: 'Answer',
        interviewExpectedAnswer: 'Expected',
        sheet: 'Python',
        grade: 'Junior',
        section: 'Core',
        subsection: 'Syntax',
        publishStatus: 'Draft',
        resources: [{ resourceId: 1, context: 'Read this' }],
      })
      .subscribe((question) => {
        resultId = question.id;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items'));
    expect(req.request.method).toBe('POST');
    expect(req.request.body.resources).toEqual([{ resourceId: 1, context: 'Read this' }]);
    req.flush({
      id: 7,
      question: 'Question',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected',
      sheet: 'Python',
      grade: 'Junior',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Draft',
      resources: [],
    });

    expect(resultId).toBe(7);
  });

  it('updateQuestion puts payload to detail endpoint and maps saved detail', () => {
    let resultQuestion: string | undefined;

    service
      .updateQuestion(7, {
        question: 'Updated',
        answer: 'Answer',
        interviewExpectedAnswer: 'Expected',
        sheet: 'Python',
        grade: 'Junior',
        section: 'Core',
        subsection: 'Syntax',
        publishStatus: 'Published',
        resources: [{ resource: { name: 'Docs', url: 'https://example.com' }, context: '' }],
      })
      .subscribe((question) => {
        resultQuestion = question.question;
      });

    const req = httpMock.expectOne((r) => r.url.endsWith('/api/competency-matrix/items/detail/7'));
    expect(req.request.method).toBe('PUT');
    expect(req.request.body.resources).toEqual([
      { resource: { name: 'Docs', url: 'https://example.com' }, context: '' },
    ]);
    req.flush({
      id: 7,
      question: 'Updated',
      answer: 'Answer',
      interviewExpectedAnswer: 'Expected',
      sheet: 'Python',
      grade: 'Junior',
      section: 'Core',
      subsection: 'Syntax',
      publishStatus: 'Published',
      resources: [],
    });

    expect(resultQuestion).toBe('Updated');
  });
});
