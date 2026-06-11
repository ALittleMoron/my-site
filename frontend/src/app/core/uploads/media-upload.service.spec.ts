import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { ApiClient } from '../http/api-client.service';
import { UnsignedUploadService } from '../http/unsigned-upload.service';
import { MediaUploadService } from './media-upload.service';

describe('MediaUploadService', () => {
  let service: MediaUploadService;
  let httpMock: HttpTestingController;
  let unsignedUpload: { putBlob: jest.Mock };

  beforeEach(() => {
    unsignedUpload = { putBlob: jest.fn().mockReturnValue(of(undefined)) };

    TestBed.configureTestingModule({
      providers: [
        MediaUploadService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: UnsignedUploadService, useValue: unsignedUpload },
      ],
    });

    service = TestBed.inject(MediaUploadService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('presigns and uploads a file, returning the public access URL', () => {
    let accessUrl: string | undefined;
    const file = new File(['image'], 'cover.png', { type: 'image/png' });

    service.uploadMediaFile(file).subscribe((url) => {
      accessUrl = url;
    });

    const presignReq = httpMock.expectOne((request) =>
      request.url.endsWith('/api/admin/files/presign-put'),
    );
    expect(presignReq.request.params.get('contentType')).toBe('image/png');
    presignReq.flush({
      uploadUrl: 'https://uploads.example.com/object',
      accessUrl: 'https://cdn.example.com/object',
    });

    expect(unsignedUpload.putBlob).toHaveBeenCalledWith(
      'https://uploads.example.com/object',
      file,
      'image/png',
    );
    expect(accessUrl).toBe('https://cdn.example.com/object');
  });
});
