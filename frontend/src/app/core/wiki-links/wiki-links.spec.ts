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
      parseWikiLinks('Read [[notes:typed-notes]] and [[matrix:angular-forms|Angular forms]].'),
    ).toEqual([
      {
        type: 'notes',
        slug: 'typed-notes',
        label: 'typed-notes',
        raw: '[[notes:typed-notes]]',
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
      parseWikiLinks('Read [[typed-notes]], [[unknown:typed-notes]], and [[notes:OK]].'),
    ).toEqual([]);
  });

  it('reports missing typed targets once', () => {
    const missing = findMissingWikiLinkTargets({
      markdown:
        'Read [[notes:typed-notes]], [[matrix:missing-question]], and [[matrix:missing-question|again]].',
      availableTargets: createWikiLinkTargetLookup([
        { type: 'notes', slugs: ['typed-notes'] },
        { type: 'matrix', slugs: ['known-question'] },
      ]),
    });

    expect(missing).toEqual(['matrix:missing-question']);
  });

  it('renders typed wiki links as sanitized localized internal links', () => {
    const html = renderMarkdownWithWikiLinks(
      'Read [[notes:typed-notes]] and [[matrix:angular-forms|Angular forms]].',
      'ru',
      sanitizeHtml,
    );

    expect(html).toContain('<a href="/ru/notes/typed-notes">typed-notes</a>');
    expect(html).toContain(
      '<a href="/ru/competency-matrix/questions/angular-forms">Angular forms</a>',
    );
  });

  it('keeps unsupported wiki links as plain text', () => {
    const html = renderMarkdownWithWikiLinks(
      'Read [[typed-notes]] and [[unknown:slug]].',
      'en',
      sanitizeHtml,
    );

    expect(html).not.toContain('href="/en/notes/typed-notes"');
    expect(html).toContain('[[typed-notes]]');
    expect(html).toContain('[[unknown:slug]]');
  });
});
