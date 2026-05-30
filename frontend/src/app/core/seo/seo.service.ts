import { Injectable, effect, inject } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';
import { environment } from '../../../environments/environment';
import { I18nService } from '../i18n/i18n.service';

export interface SeoMeta {
  title: string;
  description: string;
  canonicalUrl?: string;
  canonicalPath?: string;
  ogImage?: string;
}

export interface TranslatedSeoMeta {
  titleKey: string;
  descriptionKey: string;
  canonicalUrl?: string;
  canonicalPath?: string;
  ogImage?: string;
}

const SITE_NAME_KEY = 'app.siteName';
const DEFAULT_OG_IMAGE = '/images/personal.jpg';

@Injectable({ providedIn: 'root' })
export class SeoService {
  private readonly title = inject(Title);
  private readonly meta = inject(Meta);
  private readonly i18n = inject(I18nService);
  private translatedMeta: TranslatedSeoMeta | null = null;

  constructor() {
    effect(() => {
      this.i18n.language();
      if (this.translatedMeta) {
        this.applyTranslatedMeta(this.translatedMeta);
      }
    });
  }

  setMeta(data: SeoMeta): void {
    this.translatedMeta = null;
    this.applyMeta(data, this.i18n.translate(SITE_NAME_KEY));
  }

  setTranslatedMeta(data: TranslatedSeoMeta): void {
    this.translatedMeta = data;
    this.applyTranslatedMeta(data);
  }

  private applyTranslatedMeta(data: TranslatedSeoMeta): void {
    this.applyMeta(
      {
        title: this.i18n.translate(data.titleKey),
        description: this.i18n.translate(data.descriptionKey),
        canonicalUrl: data.canonicalUrl,
        canonicalPath: data.canonicalPath,
        ogImage: data.ogImage,
      },
      this.i18n.translate('app.siteName'),
    );
  }

  private applyMeta(data: SeoMeta, siteName: string): void {
    const fullTitle = `${data.title} - ${siteName}`;
    const image = data.ogImage ?? DEFAULT_OG_IMAGE;
    const url = data.canonicalUrl ?? this.buildCanonicalUrl(data.canonicalPath);

    this.title.setTitle(fullTitle);

    this.meta.updateTag({ name: 'description', content: data.description });

    this.meta.updateTag({ property: 'og:type', content: 'website' });
    this.meta.updateTag({ property: 'og:site_name', content: siteName });
    this.meta.updateTag({ property: 'og:title', content: fullTitle });
    this.meta.updateTag({ property: 'og:description', content: data.description });
    this.meta.updateTag({ property: 'og:url', content: url });
    this.meta.updateTag({ property: 'og:image', content: image });

    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: fullTitle });
    this.meta.updateTag({ name: 'twitter:description', content: data.description });

    if (url) {
      this.updateCanonicalLink(url);
    } else {
      this.removeCanonicalLink();
    }
  }

  private buildCanonicalUrl(path: string | undefined): string {
    if (!path) return '';
    const baseUrl = environment.siteUrl.replace(/\/$/, '');
    if (!baseUrl) return path;
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${baseUrl}${normalizedPath}`;
  }

  private updateCanonicalLink(url: string): void {
    const head = document.head;
    let link = head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!link) {
      link = document.createElement('link');
      link.setAttribute('rel', 'canonical');
      head.appendChild(link);
    }
    link.setAttribute('href', url);
  }

  private removeCanonicalLink(): void {
    document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')?.remove();
  }
}
