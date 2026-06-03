import {
  findMissingNoteWikiLinkSlugs,
  parseNoteWikiLinks,
  renderNoteMarkdown,
} from './note-wiki-links';

describe('note wiki links', () => {
  it('parses slug-only and labelled wiki links', () => {
    expect(parseNoteWikiLinks('Read [[typed-notes]] and [[angular-forms|Angular forms]].')).toEqual(
      [
        { slug: 'typed-notes', label: 'typed-notes', raw: '[[typed-notes]]' },
        {
          slug: 'angular-forms',
          label: 'Angular forms',
          raw: '[[angular-forms|Angular forms]]',
        },
      ],
    );
  });

  it('reports missing linked note slugs once', () => {
    const missing = findMissingNoteWikiLinkSlugs({
      markdown: 'Read [[typed-notes]], [[missing-note]], and [[missing-note|again]].',
      availableSlugs: new Set(['typed-notes']),
    });

    expect(missing).toEqual(['missing-note']);
  });

  it('renders wiki links as sanitized internal note links', () => {
    const html = renderNoteMarkdown(
      'Read [[typed-notes]] and [[angular-forms|Angular forms]].',
      'ru',
    );

    expect(html).toContain('<a href="/ru/notes/typed-notes">typed-notes</a>');
    expect(html).toContain('<a href="/ru/notes/angular-forms">Angular forms</a>');
  });

  it('renders wiki links with the active language prefix', () => {
    const html = renderNoteMarkdown('Read [[typed-notes]].', 'en');

    expect(html).toContain('<a href="/en/notes/typed-notes">typed-notes</a>');
  });
});
