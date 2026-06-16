import {
  createWikiLinkTargetLookup,
  findMissingWikiLinkTargets,
  parseWikiLinks,
  renderMarkdownWithWikiLinks,
} from './wiki-links';

describe('wiki links', () => {
  const sanitizeHtml = (html: string): string => html;

  it('parses typed slug-only and labelled links', () => {
    expect(
      parseWikiLinks(
        'Read [[articles:typed-articles]] and [[matrix:angular-forms|Angular forms]].',
      ),
    ).toEqual([
      {
        type: 'articles',
        slug: 'typed-articles',
        label: 'typed-articles',
        raw: '[[articles:typed-articles]]',
      },
      {
        type: 'matrix',
        slug: 'angular-forms',
        label: 'Angular forms',
        raw: '[[matrix:angular-forms|Angular forms]]',
      },
    ]);
  });

  it('ignores legacy untyped and unknown-prefixed wiki links', () => {
    expect(
      parseWikiLinks('Read [[typed-articles]], [[unknown:typed-articles]], and [[articles:OK]].'),
    ).toEqual([]);
  });

  it('reports missing typed targets once', () => {
    const missing = findMissingWikiLinkTargets({
      markdown:
        'Read [[articles:typed-articles]], [[matrix:missing-question]], and [[matrix:missing-question|again]].',
      availableTargets: createWikiLinkTargetLookup([
        { type: 'articles', slugs: ['typed-articles'] },
        { type: 'matrix', slugs: ['known-question'] },
      ]),
    });

    expect(missing).toEqual(['matrix:missing-question']);
  });

  it('renders typed wiki links as sanitized localized internal links', () => {
    const html = renderMarkdownWithWikiLinks(
      'Read [[articles:typed-articles]] and [[matrix:angular-forms|Angular forms]].',
      'ru',
      sanitizeHtml,
    );

    expect(html).toContain('<a href="/ru/articles/typed-articles">typed-articles</a>');
    expect(html).toContain(
      '<a href="/ru/competency-matrix/questions/angular-forms">Angular forms</a>',
    );
  });

  it('keeps unsupported wiki links as plain text', () => {
    const html = renderMarkdownWithWikiLinks(
      'Read [[typed-articles]] and [[unknown:slug]].',
      'en',
      sanitizeHtml,
    );

    expect(html).not.toContain('href="/en/articles/typed-articles"');
    expect(html).toContain('[[typed-articles]]');
    expect(html).toContain('[[unknown:slug]]');
  });
});
