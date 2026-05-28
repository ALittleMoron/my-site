import { Injectable, inject } from '@angular/core';
import { Observable, switchMap, map } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { UnsignedUploadService } from '../../../core/http/unsigned-upload.service';

interface PresignPutResponseDto {
  uploadUrl: string;
  accessUrl: string;
}

@Injectable({ providedIn: 'root' })
export class FileUploadService {
  private readonly api = inject(ApiClient);
  private readonly unsignedUpload = inject(UnsignedUploadService);

  uploadEditorImage(blob: Blob): Observable<string> {
    const contentType = blob.type || 'application/octet-stream';
    return this.api
      .get<PresignPutResponseDto>('/api/files/presign-put', { contentType })
      .pipe(
        switchMap((presign) =>
          this.unsignedUpload
            .putBlob(presign.uploadUrl, blob, contentType)
            .pipe(map(() => presign.accessUrl)),
        ),
      );
  }
}
