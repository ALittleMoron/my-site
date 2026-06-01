import {
  NOTE_SEO_ANALYSIS_RULES,
  NoteSeoCheckId,
  NoteSeoInput,
  analyzeNoteSeo,
} from './note-seo-analysis';

describe('analyzeNoteSeo', () => {
  it('returns a good analysis for a complete note', () => {
    const analysis = analyzeNoteSeo({
      input: noteSeoInput({}),
      rules: NOTE_SEO_ANALYSIS_RULES,
    });

    expect(analysis.overallStatus).toBe('good');
    expect(analysis.canonicalPath).toBe('/notes/typed-notes');
    expect(analysis.checks.every((check) => check.status === 'good')).toBe(true);
  });

  it('warns when slug format is not URL friendly', () => {
    const analysis = analyzeNoteSeo({
      input: noteSeoInput({ slug: 'Typed Notes!' }),
      rules: NOTE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'slug-format')).toBe('warning');
    expect(analysis.overallStatus).toBe('warning');
  });

  it('warns when content is too short to build a useful description', () => {
    const analysis = analyzeNoteSeo({
      input: noteSeoInput({ content: 'Too short.' }),
      rules: NOTE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'content-length')).toBe('warning');
    expect(checkStatus(analysis, 'description-quality')).toBe('warning');
  });

  it('warns when markdown content adds another page-level H1', () => {
    const analysis = analyzeNoteSeo({
      input: noteSeoInput({
        content: `# Duplicate heading

This note has enough useful words for a reader and a generated search snippet, but the markdown heading would create a second page-level heading next to the visible note title.`,
      }),
      rules: NOTE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'single-h1')).toBe('warning');
  });

  it('warns when no active tags are attached', () => {
    const analysis = analyzeNoteSeo({
      input: noteSeoInput({ tags: [] }),
      rules: NOTE_SEO_ANALYSIS_RULES,
    });

    expect(checkStatus(analysis, 'active-tags')).toBe('warning');
    expect(analysis.overallStatus).toBe('warning');
  });
});

function checkStatus(
  analysis: ReturnType<typeof analyzeNoteSeo>,
  checkId: NoteSeoCheckId,
): 'good' | 'warning' | 'missing' {
  const check = analysis.checks.find((item) => item.id === checkId);
  if (!check) {
    throw new Error(`Missing check ${checkId}`);
  }
  return check.status;
}

function noteSeoInput(params: Partial<NoteSeoInput>): NoteSeoInput {
  return {
    slug: 'typed-notes',
    title: 'Typed notes for Angular search',
    content:
      'This note explains how typed Angular forms, signals, markdown content, and localized fields work together in the notes editor for the portfolio knowledge base.',
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
