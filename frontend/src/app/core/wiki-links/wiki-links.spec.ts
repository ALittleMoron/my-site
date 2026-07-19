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

  it('renders real syntax tokens for multiple supported fenced code blocks', () => {
    const html = renderMarkdownWithWikiLinks(
      [
        '```ts',
        'const answer: number = 42;',
        '```',
        '',
        '```python',
        'def answer():',
        '    return 42',
        '```',
      ].join('\n'),
      'en',
      sanitizeHtml,
    );

    expect(html).toContain('<code class="language-ts">');
    expect(html).toContain('<code class="language-python">');
    expect(html).toContain('<span class="token keyword">const</span>');
    expect(html).toContain('<span class="token keyword">def</span>');
  });

  it.each([
    { language: 'js', code: 'const value = 1;' },
    { language: 'sh', code: 'echo "$HOME"' },
    { language: 'dockerfile', code: 'FROM python:3.14' },
    { language: 'yml', code: 'enabled: true' },
  ])('highlights the $language language alias', ({ language, code }) => {
    const html = renderMarkdownWithWikiLinks(
      `\`\`\`${language}\n${code}\n\`\`\``,
      'en',
      sanitizeHtml,
    );

    expect(html).toContain(`class="language-${language}"`);
    expect(html).toContain('class="token ');
  });

  it.each(['', 'unknown-language'])(
    'keeps an unsupported "%s" fenced code block as escaped plain code',
    (language) => {
      const html = renderMarkdownWithWikiLinks(
        `\`\`\`${language}\n<script>alert("code")</script>\n\`\`\``,
        'en',
        sanitizeHtml,
      );

      expect(html).toContain('<pre class="markdown-code"><code');
      expect(html).toContain('&lt;script&gt;alert(&quot;code&quot;)&lt;/script&gt;');
      expect(html).not.toContain('<span class="token ');
    },
  );
});
