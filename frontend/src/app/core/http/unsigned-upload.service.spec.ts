import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { UnsignedUploadService } from './unsigned-upload.service';

describe('UnsignedUploadService', () => {
  let service: UnsignedUploadService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [UnsignedUploadService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(UnsignedUploadService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('puts a blob to an absolute presigned URL and emits void', () => {
    const blob = new Blob(['image'], { type: 'image/png' });
    let completed = false;

    service.putBlob('https://storage.example.com/upload', blob, 'image/png').subscribe(() => {
      completed = true;
    });

    const req = httpMock.expectOne('https://storage.example.com/upload');
    expect(req.request.method).toBe('PUT');
    expect(req.request.headers.get('Content-Type')).toBe('image/png');
    expect(req.request.body).toBe(blob);
    req.flush('');

    expect(completed).toBe(true);
  });
});
