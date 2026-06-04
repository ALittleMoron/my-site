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
      'Read <img src=x onerror="alert(1)"> and [[notes:typed-notes|typed note]].',
      'en',
    );

    expect(html).toContain('<a href="/en/notes/typed-notes">typed note</a>');
    expect(html).not.toContain('onerror');
  });
});
