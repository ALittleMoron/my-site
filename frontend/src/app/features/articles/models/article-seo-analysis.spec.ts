import {
  ARTICLE_SEO_ANALYSIS_RULES,
  ArticleSeoCheckId,
  ArticleSeoInput,
  analyzeArticleSeo,
} from './article-seo-analysis';

describe('analyzeArticleSeo', () => {
  it('returns a good analysis for a complete article', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({}),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(analysis.overallStatus).toBe('good');
    expect(analysis.canonicalPath).toBe('/articles/typed-articles');
    expect(analysis.checks.every((check) => check.status === 'good')).toBe(true);
  });

  it('warns when slug format is not URL friendly', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({ slug: 'Typed Articles!' }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'slug-format')).toBe('warning');
    expect(analysis.overallStatus).toBe('warning');
  });

  it('warns when content is too short to build a useful description', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({ content: 'Too short.' }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'content-length')).toBe('warning');
    expect(checkStatus(analysis, 'description-quality')).toBe('warning');
  });

  it('warns when markdown content adds another page-level H1', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({
        content: `# Duplicate heading

This article has enough useful words for a reader and a generated search snippet, but the markdown heading would create a second page-level heading next to the visible article title.`,
      }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'single-h1')).toBe('warning');
  });

  it('warns when no active tags are attached', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({ tags: [] }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'active-tags')).toBe('warning');
    expect(analysis.overallStatus).toBe('warning');
  });

  it('reports missing SEO metadata as advisory missing checks', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({
        seoTitle: null,
        seoDescription: null,
        coverImageUrl: null,
        coverImageAlt: null,
      }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'seo-title')).toBe('missing');
    expect(checkStatus(analysis, 'seo-description')).toBe('missing');
    expect(checkStatus(analysis, 'cover-image')).toBe('missing');
    expect(checkStatus(analysis, 'cover-image-alt')).toBe('missing');
    expect(analysis.overallStatus).toBe('missing');
  });

  it('warns when SEO metadata length is outside useful search and social ranges', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({
        seoTitle: 'Short',
        seoDescription: 'Short description.',
        coverImageAlt: 'x',
      }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'seo-title')).toBe('warning');
    expect(checkStatus(analysis, 'seo-description')).toBe('warning');
    expect(checkStatus(analysis, 'cover-image-alt')).toBe('warning');
  });

  it('warns when wiki links point to missing typed targets', () => {
    const analysis = analyzeArticleSeo({
      input: articleSeoInput({ missingWikiLinkTargets: ['matrix:missing-question'] }),
      rules: ARTICLE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'wiki-links')).toBe('warning');
  });
});

function checkStatus(
  analysis: ReturnType<typeof analyzeArticleSeo>,
  checkId: ArticleSeoCheckId,
): 'good' | 'warning' | 'missing' {
  const check = analysis.checks.find((item) => item.id === checkId);
  if (!check) {
    throw new Error(`Missing check ${checkId}`);
  }
  return check.status;
}

function articleSeoInput(params: Partial<ArticleSeoInput>): ArticleSeoInput {
  return {
    slug: 'typed-articles',
    title: 'Typed articles for Angular search',
    content:
      'This article explains how typed Angular forms, signals, markdown content, and localized fields work together in the articles editor for the portfolio knowledge base.',
    seoTitle: 'Typed articles for Angular search and social previews',
    seoDescription:
      'A practical article about Angular typed forms, signals, markdown content, and localized article fields in the articles editor.',
    coverImageUrl: 'https://example.com/cover.jpg',
    coverImageAlt: 'Article cover with Angular form controls',
    missingWikiLinkTargets: [],
    folder: 'Engineering',
    language: 'en',
    tags: [
      {
        id: 1,
        name: 'Angular',
        slug: 'angular',
        deletedAt: null,
        translations: { ru: { name: 'Angular' }, en: { name: 'Angular' } },
      },
    ],
    ...params,
  };
}
