import { Injectable, inject } from '@angular/core';
import { Meta, Title } from '@angular/platform-browser';

export interface SeoMeta {
  title: string;
  description: string;
  canonicalUrl?: string;
  ogImage?: string;
}

const SITE_NAME = 'Мой сайт';
const DEFAULT_OG_IMAGE = '/images/personal.jpg';

@Injectable({ providedIn: 'root' })
export class SeoService {
  private readonly title = inject(Title);
  private readonly meta = inject(Meta);

  setMeta(data: SeoMeta): void {
    const fullTitle = `${data.title} - ${SITE_NAME}`;
    const image = data.ogImage ?? DEFAULT_OG_IMAGE;
    const url = data.canonicalUrl ?? '';

    this.title.setTitle(fullTitle);

    this.meta.updateTag({ name: 'description', content: data.description });

    this.meta.updateTag({ property: 'og:type', content: 'website' });
    this.meta.updateTag({ property: 'og:site_name', content: SITE_NAME });
    this.meta.updateTag({ property: 'og:title', content: fullTitle });
    this.meta.updateTag({ property: 'og:description', content: data.description });
    this.meta.updateTag({ property: 'og:url', content: url });
    this.meta.updateTag({ property: 'og:image', content: image });

    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: fullTitle });
    this.meta.updateTag({ name: 'twitter:description', content: data.description });

    if (url) {
      this.updateCanonicalLink(url);
    }
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
}
