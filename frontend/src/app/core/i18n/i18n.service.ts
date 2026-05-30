import { DOCUMENT } from '@angular/common';
import { Injectable, Injector, inject, signal } from '@angular/core';
import { Observable, catchError, map, of, switchMap, tap, throwError } from 'rxjs';
import { ApiClient } from '../http/api-client.service';
import {
  I18nBundleDto,
  I18nLanguage,
  I18nLanguagesDto,
  I18nParams,
  LanguageCode,
  isLanguageCode,
} from './i18n.model';

const STORAGE_KEY = 'chosenLanguage';
const STARTUP_ERROR_MESSAGES: Record<string, string> = {
  'i18n.startupError.title': 'Failed to load localization',
  'i18n.startupError.message': 'Check the API connection and try again.',
  'i18n.startupError.retry': 'Retry',
};

@Injectable({ providedIn: 'root' })
export class I18nService {
  private readonly injector = inject(Injector);
  private readonly document = inject(DOCUMENT);
  private readonly bundleCache = new Map<LanguageCode, Record<string, string>>();
  private readonly messages = signal<Record<string, string> | null>(null);

  readonly language = signal<LanguageCode | null>(null);
  readonly languages = signal<I18nLanguage[]>([]);
  readonly startupError = signal(false);

  initialize(): Observable<void> {
    this.startupError.set(false);
    return this.api()
      .get<I18nLanguagesDto>('/api/i18n/languages')
      .pipe(
        switchMap((response) => {
          this.languages.set(response.languages);
          return this.loadLanguage(this.resolveInitialLanguage(response), true);
        }),
        catchError(() => {
          this.startupError.set(true);
          return of(void 0);
        }),
      );
  }

  retryStartup(): Observable<void> {
    return this.initialize();
  }

  switchLanguage(language: LanguageCode): Observable<void> {
    if (!this.isAvailableLanguage(language)) {
      return throwError(() => new Error(`Unsupported language: ${language}`));
    }
    return this.loadLanguage(language, true);
  }

  translate(key: string, params?: I18nParams): string {
    const template = this.messages()?.[key] ?? STARTUP_ERROR_MESSAGES[key] ?? key;
    if (!params) return template;
    return Object.entries(params).reduce(
      (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
      template,
    );
  }

  enumGradeKey(grade: string): string {
    const normalized = grade.replace('+', 'Plus');
    return `enum.grade.${normalized}`;
  }

  dateLocale(): string {
    return this.language() === 'en' ? 'en-US' : 'ru-RU';
  }

  private resolveInitialLanguage(response: I18nLanguagesDto): LanguageCode {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (isLanguageCode(stored) && this.includesLanguage(response.languages, stored)) {
      return stored;
    }
    if (this.includesLanguage(response.languages, response.defaultLanguage)) {
      return response.defaultLanguage;
    }
    throw new Error(`Unsupported default language: ${response.defaultLanguage}`);
  }

  private loadLanguage(language: LanguageCode, persist: boolean): Observable<void> {
    const cached = this.bundleCache.get(language);
    if (cached) {
      this.applyBundle(language, cached, persist);
      return of(void 0);
    }
    return this.api()
      .get<I18nBundleDto>(`/api/i18n/bundles/${language}`)
      .pipe(
        tap((bundle) => {
          this.bundleCache.set(bundle.language, bundle.messages);
          this.applyBundle(bundle.language, bundle.messages, persist);
        }),
        map(() => void 0),
      );
  }

  private applyBundle(
    language: LanguageCode,
    messages: Record<string, string>,
    persist: boolean,
  ): void {
    if (persist) {
      localStorage.setItem(STORAGE_KEY, language);
    }
    this.messages.set(messages);
    this.language.set(language);
    this.startupError.set(false);
    this.document.documentElement.lang = language;
  }

  private isAvailableLanguage(language: LanguageCode): boolean {
    return this.includesLanguage(this.languages(), language);
  }

  private includesLanguage(languages: readonly I18nLanguage[], language: LanguageCode): boolean {
    return languages.some((item) => item.code === language);
  }

  private api(): ApiClient {
    return this.injector.get(ApiClient);
  }
}
