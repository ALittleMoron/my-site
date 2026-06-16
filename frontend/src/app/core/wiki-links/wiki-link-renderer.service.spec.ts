import { TestBed } from '@angular/core/testing';
import { WikiLinkRendererService } from './wiki-link-renderer.service';

describe('WikiLinkRendererService', () => {
  let service: WikiLinkRendererService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [WikiLinkRendererService],
    });
    service = TestBed.inject(WikiLinkRendererService);
  });

  it('renders typed wiki links as sanitized localized internal links', () => {
    const html = service.render(
      'Read <img src=x onerror="alert(1)"> and [[articles:typed-articles|typed article]].',
      'en',
    );

    expect(html).toContain('<a href="/en/articles/typed-articles">typed article</a>');
    expect(html).not.toContain('onerror');
  });
});
