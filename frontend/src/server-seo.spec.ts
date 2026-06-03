import {
  buildArticleNotFoundHtml,
  buildPublicArticleApiUrl,
  parsePublicArticlePath,
} from './server-seo';

describe('server SEO helpers', () => {
  it('parses language-prefixed public article URLs', () => {
    expect(parsePublicArticlePath('/ru/notes/typed-notes')).toEqual({
      language: 'ru',
      slug: 'typed-notes',
    });
    expect(parsePublicArticlePath('/en/notes/angular-ssr')).toEqual({
      language: 'en',
      slug: 'angular-ssr',
    });
  });

  it('ignores non-public article URLs', () => {
    expect(parsePublicArticlePath('/notes/typed-notes')).toBeNull();
    expect(parsePublicArticlePath('/ru/notes')).toBeNull();
    expect(parsePublicArticlePath('/ru/admin/notes/typed-notes')).toBeNull();
    expect(parsePublicArticlePath('/de/notes/typed-notes')).toBeNull();
  });

  it('builds public article API URL with explicit published-only visibility', () => {
    const url = buildPublicArticleApiUrl('https://api.example.com', {
      language: 'ru',
      slug: 'typed-notes',
    });

    expect(url.toString()).toBe(
      'https://api.example.com/api/notes/detail/typed-notes?language=ru&onlyPublished=true',
    );
  });

  it('builds noindex HTML for missing public article URLs', () => {
    const html = buildArticleNotFoundHtml('https://example.com', {
      language: 'en',
      slug: 'missing-note',
    });

    expect(html).toContain('<title>Article not found</title>');
    expect(html).toContain('<meta name="robots" content="noindex, follow">');
    expect(html).toContain(
      '<link rel="canonical" href="https://example.com/en/notes/missing-note">',
    );
  });
});
