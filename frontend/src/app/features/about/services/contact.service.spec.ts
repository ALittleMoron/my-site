import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ContactService } from './contact.service';
import { ApiClient } from '../../../core/http/api-client.service';
import { ContactRequest } from '../models/contact.model';

describe('ContactService', () => {
  let service: ContactService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ContactService, ApiClient, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(ContactService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('calls POST /api/contacts with the request body', () => {
    const request: ContactRequest = {
      name: 'Alice',
      email: 'alice@example.com',
      telegram: null,
      message: 'Hello there',
    };

    let completed = false;
    service.createContactRequest(request).subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne(r => r.url.endsWith('/api/contacts'));
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(request);
    req.flush(null, { status: 204, statusText: 'No Content' });

    expect(completed).toBe(true);
  });
});
