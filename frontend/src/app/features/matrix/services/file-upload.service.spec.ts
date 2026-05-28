import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { of } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { UnsignedUploadService } from '../../../core/http/unsigned-upload.service';
import { FileUploadService } from './file-upload.service';

describe('FileUploadService', () => {
  let service: FileUploadService;
  let httpMock: HttpTestingController;
  let unsignedUpload: { putBlob: jest.Mock };

  beforeEach(() => {
    unsignedUpload = { putBlob: jest.fn().mockReturnValue(of(undefined)) };
    TestBed.configureTestingModule({
      providers: [
        FileUploadService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: UnsignedUploadService, useValue: unsignedUpload },
      ],
    });
    service = TestBed.inject(FileUploadService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('presigns, uploads the blob, and returns accessUrl', () => {
    let result: string | undefined;
    const blob = new Blob(['image'], { type: 'image/png' });

    service.uploadEditorImage(blob).subscribe((accessUrl) => {
      result = accessUrl;
    });

    const presignReq = httpMock.expectOne((r) => r.url.endsWith('/api/files/presign-put'));
    expect(presignReq.request.method).toBe('GET');
    expect(presignReq.request.params.get('contentType')).toBe('image/png');
    presignReq.flush({
      uploadUrl: 'https://storage.example.com/upload',
      accessUrl: 'https://cdn.example.com/image.png',
    });

    expect(unsignedUpload.putBlob).toHaveBeenCalledWith(
      'https://storage.example.com/upload',
      blob,
      'image/png',
    );
    expect(result).toBe('https://cdn.example.com/image.png');
  });
});
