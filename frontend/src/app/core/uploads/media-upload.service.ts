import { Injectable, inject } from '@angular/core';
import { Observable, map, switchMap } from 'rxjs';
import { ApiClient } from '../http/api-client.service';
import { UnsignedUploadService } from '../http/unsigned-upload.service';

interface PresignPutResponseDto {
  uploadUrl: string;
  accessUrl: string;
}

@Injectable({ providedIn: 'root' })
export class MediaUploadService {
  private readonly api = inject(ApiClient);
  private readonly unsignedUpload = inject(UnsignedUploadService);

  uploadMediaFile(file: Blob): Observable<string> {
    const contentType = file.type || 'application/octet-stream';
    return this.api
      .get<PresignPutResponseDto>('/api/admin/files/presign-put', { contentType })
      .pipe(
        switchMap((presign) =>
          this.unsignedUpload
            .putBlob(presign.uploadUrl, file, contentType)
            .pipe(map(() => presign.accessUrl)),
        ),
      );
  }
}
