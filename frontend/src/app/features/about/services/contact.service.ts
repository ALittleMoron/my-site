import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiClient } from '../../../core/http/api-client.service';
import { ContactRequest } from '../models/contact.model';

@Injectable({ providedIn: 'root' })
export class ContactService {
  private readonly api = inject(ApiClient);

  createContactRequest(request: ContactRequest): Observable<void> {
    return this.api.post<void>('/api/contacts', request);
  }
}
