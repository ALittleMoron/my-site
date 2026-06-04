import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ApiClient } from '../http/api-client.service';
import { LanguageCode } from '../i18n/i18n.model';
import {
  WikiLinkTargetGroup,
  WikiLinkTargetLookup,
  createWikiLinkTargetLookup,
} from './wiki-links';

interface WikiLinkTargetsDto {
  targets: WikiLinkTargetGroup[];
}

@Injectable({ providedIn: 'root' })
export class WikiLinkTargetsService {
  private readonly api = inject(ApiClient);

  getTargets(language: LanguageCode): Observable<WikiLinkTargetLookup> {
    return this.api
      .get<WikiLinkTargetsDto>('/api/wiki-links/targets', { language })
      .pipe(map((dto) => createWikiLinkTargetLookup(dto.targets)));
  }
}
