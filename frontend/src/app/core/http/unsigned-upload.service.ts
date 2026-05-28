import { HttpBackend, HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UnsignedUploadService {
  private readonly http = new HttpClient(inject(HttpBackend));

  putBlob(uploadUrl: string, blob: Blob, contentType: string): Observable<void> {
    return this.http
      .put(uploadUrl, blob, {
        headers: { 'Content-Type': contentType },
        responseType: 'text',
      })
      .pipe(map(() => undefined));
  }
}
