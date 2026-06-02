import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { MediaUploadService } from '../uploads/media-upload.service';

@Injectable({ providedIn: 'root' })
export class EditorImageUploadService {
  private readonly mediaUpload = inject(MediaUploadService);

  uploadEditorImage(blob: Blob): Observable<string> {
    return this.mediaUpload.uploadMediaFile(blob);
  }
}
