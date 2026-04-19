import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { MatrixService } from './matrix.service';
import { ApiClient } from '../../../core/http/api-client.service';
import { MatrixQuestion } from '../models/matrix-question.model';

const mockQuestion: MatrixQuestion = {
  id: '1',
  title: 'What is a closure?',
  description: 'Explain JS closures.',
  grade: 'junior',
  topic: 'JavaScript',
  is_published: true,
};

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

  describe('getQuestions', () => {
    it('should GET /api/matrix/questions without search param when not provided', () => {
      let result: MatrixQuestion[] | undefined;
      service.getQuestions().subscribe(q => (result = q));

      const req = httpMock.expectOne(r => r.url.includes('/api/matrix/questions'));
      expect(req.request.method).toBe('GET');
      expect(req.request.params.has('search')).toBe(false);
      req.flush([mockQuestion]);

      expect(result).toEqual([mockQuestion]);
    });

    it('should include search query param when provided', () => {
      service.getQuestions('closure').subscribe();

      const req = httpMock.expectOne(r => r.url.includes('/api/matrix/questions'));
      expect(req.request.params.get('search')).toBe('closure');
      req.flush([]);
    });

    it('should return empty array when response is empty', () => {
      let result: MatrixQuestion[] | undefined;
      service.getQuestions().subscribe(q => (result = q));

      const req = httpMock.expectOne(r => r.url.includes('/api/matrix/questions'));
      req.flush([]);

      expect(result).toEqual([]);
    });
  });

  describe('getQuestion', () => {
    it('should GET /api/matrix/questions/:id', () => {
      let result: MatrixQuestion | undefined;
      service.getQuestion('1').subscribe(q => (result = q));

      const req = httpMock.expectOne(r => r.url.includes('/api/matrix/questions/1'));
      expect(req.request.method).toBe('GET');
      req.flush(mockQuestion);

      expect(result).toEqual(mockQuestion);
    });
  });
});
