import { groupUpdateEntries, UPDATES_TIMELINE_ENTRIES } from './updates.timeline';

describe('updates timeline', () => {
  it('groups localized flat entries by month in reverse chronological order', () => {
    const groups = groupUpdateEntries(
      [
        {
          id: 'older',
          month: '2026-05',
          order: 20,
          title: { ru: 'Старое', en: 'Older' },
          summary: { ru: 'Старое описание', en: 'Older summary' },
          tagIds: ['content'],
        },
        {
          id: 'newer-second',
          month: '2026-07',
          order: 20,
          title: { ru: 'Новое второе', en: 'Newer second' },
          summary: { ru: 'Новое второе описание', en: 'Newer second summary' },
          tagIds: ['frontend'],
        },
        {
          id: 'newer-first',
          month: '2026-07',
          order: 10,
          title: { ru: 'Новое первое', en: 'Newer first' },
          summary: { ru: 'Новое первое описание', en: 'Newer first summary' },
          tagIds: ['frontend'],
        },
      ],
      'ru',
      'ru-RU',
    );

    expect(groups.map((group) => group.datetime)).toEqual(['2026-07', '2026-05']);
    expect(groups[0]?.label).toBe('Июль 2026');
    expect(groups[0]?.entries.map((entry) => entry.id)).toEqual(['newer-first', 'newer-second']);
    expect(groups[1]?.entries.map((entry) => entry.id)).toEqual(['older']);
    expect(groups[0]?.entries[0]?.title).toBe('Новое первое');
    expect(groups[0]?.entries[0]?.summary).toBe('Новое первое описание');
    expect(groups[0]?.entries[0]?.tagKeys).toEqual(['updates.tag.frontend']);
  });

  it('localizes entry text and month labels without per-month i18n keys', () => {
    const groups = groupUpdateEntries(
      [
        {
          id: 'release',
          month: '2026-07',
          order: 10,
          title: { ru: 'Релиз', en: 'Release' },
          summary: { ru: 'Описание релиза', en: 'Release summary' },
          tagIds: ['delivery'],
        },
      ],
      'en',
      'en-US',
    );

    expect(groups).toEqual([
      {
        datetime: '2026-07',
        label: 'July 2026',
        entries: [
          {
            id: 'release',
            title: 'Release',
            summary: 'Release summary',
            tagKeys: ['updates.tag.delivery'],
          },
        ],
      },
    ]);
  });

  it('keeps public history spread across real site-history months', () => {
    const months = new Set(UPDATES_TIMELINE_ENTRIES.map((entry) => entry.month));

    expect(months.size).toBeGreaterThanOrEqual(10);
    expect(months.has('2024-09')).toBe(true);
    expect(months.has('2024-12')).toBe(true);
    expect(months.has('2025-04')).toBe(true);
    expect(months.has('2026-06')).toBe(true);
    expect(months.has('2026-07')).toBe(true);
  });

  it('keeps accumulating copy in typed localized content instead of backend i18n keys', () => {
    const firstEntry = UPDATES_TIMELINE_ENTRIES[0];

    expect(firstEntry?.title.ru).toBeTruthy();
    expect(firstEntry?.title.en).toBeTruthy();
    expect(firstEntry?.summary.ru).toBeTruthy();
    expect(firstEntry?.summary.en).toBeTruthy();
    expect('titleKey' in (firstEntry ?? {})).toBe(false);
    expect('summaryKey' in (firstEntry ?? {})).toBe(false);
  });

  it('includes the public changelog milestone in the current month', () => {
    const entry = UPDATES_TIMELINE_ENTRIES.find((item) => item.id === 'public-updates-page');

    expect(entry?.month).toBe('2026-07');
    expect(entry?.title.ru).toContain('журнал изменений');
    expect(entry?.title.en).toContain('updates page');
    expect(entry?.summary.ru).toContain('полной историей сайта');
    expect(entry?.summary.en).toContain('compressed site history');
    expect(entry?.tagIds).toEqual(['content', 'frontend', 'backend', 'seo']);
  });

  it('includes the July full security audit milestone', () => {
    const entry = UPDATES_TIMELINE_ENTRIES.find((item) => item.id === 'full-security-audit');

    expect(entry?.month).toBe('2026-07');
    expect(entry?.title.ru).toContain('аудит безопасности');
    expect(entry?.title.en).toContain('security audit');
    expect(entry?.summary.ru).toContain('модель угроз');
    expect(entry?.summary.en).toContain('threat model');
    expect(entry?.tagIds).toEqual(['security', 'infra', 'backend', 'frontend', 'quality']);
  });

  it('includes the July auth session hardening milestone', () => {
    const entry = UPDATES_TIMELINE_ENTRIES.find((item) => item.id === 'auth-session-hardening');

    expect(entry?.month).toBe('2026-07');
    expect(entry?.title.ru).toContain('Авторизация');
    expect(entry?.title.en).toContain('Authorization');
    expect(entry?.summary.ru).toContain('скользящие');
    expect(entry?.summary.ru).toContain('absolute lifetime');
    expect(entry?.summary.en).toContain('sliding');
    expect(entry?.summary.en).toContain('absolute lifetime');
    expect(entry?.tagIds).toEqual(['auth', 'security', 'backend', 'frontend', 'admin']);
  });

  it('renders July milestones in editorial order', () => {
    const julyGroup = groupUpdateEntries(UPDATES_TIMELINE_ENTRIES, 'ru', 'ru-RU').find(
      (group) => group.datetime === '2026-07',
    );

    expect(julyGroup?.entries.map((entry) => entry.id)).toEqual([
      'full-security-audit',
      'auth-session-hardening',
      'public-updates-page',
      'release-workflow',
    ]);
  });

  it('assigns badges only to the areas materially touched by each milestone', () => {
    const tagIdsByEntry = new Map(
      UPDATES_TIMELINE_ENTRIES.map((entry) => [entry.id, entry.tagIds] as const),
    );

    expect(tagIdsByEntry.get('public-updates-page')).toEqual([
      'content',
      'frontend',
      'backend',
      'seo',
    ]);
    expect(tagIdsByEntry.get('release-workflow')).toEqual([
      'delivery',
      'quality',
      'admin',
      'infra',
    ]);
    expect(tagIdsByEntry.get('full-security-audit')).toEqual([
      'security',
      'infra',
      'backend',
      'frontend',
      'quality',
    ]);
    expect(tagIdsByEntry.get('auth-session-hardening')).toEqual([
      'auth',
      'security',
      'backend',
      'frontend',
      'admin',
    ]);
    expect(tagIdsByEntry.get('public-seo-layer')).toEqual([
      'seo',
      'frontend',
      'backend',
      'content',
    ]);
    expect(tagIdsByEntry.get('admin-workspaces')).toEqual([
      'admin',
      'frontend',
      'backend',
      'content',
      'matrix',
    ]);
    expect(tagIdsByEntry.get('quality-ops')).toEqual(['quality', 'security', 'infra', 'delivery']);
    expect(tagIdsByEntry.get('angular-knowledge-base')).toEqual([
      'frontend',
      'content',
      'matrix',
      'localization',
      'analytics',
    ]);
    expect(tagIdsByEntry.get('angular-scaffold')).toEqual(['frontend', 'matrix']);
    expect(tagIdsByEntry.get('auth-admin-foundation')).toEqual([
      'auth',
      'backend',
      'admin',
      'matrix',
      'security',
      'infra',
    ]);
    expect(tagIdsByEntry.get('editor-uploads')).toEqual([
      'content',
      'frontend',
      'backend',
      'matrix',
      'infra',
    ]);
    expect(tagIdsByEntry.get('architecture-docs')).toEqual([
      'infra',
      'backend',
      'security',
      'auth',
      'quality',
      'localization',
    ]);
    expect(tagIdsByEntry.get('blog-ci')).toEqual(['content', 'delivery', 'quality', 'infra']);
    expect(tagIdsByEntry.get('public-prototype')).toEqual(['backend', 'frontend', 'matrix', 'seo']);
    expect(tagIdsByEntry.get('litestar-migration')).toEqual(['backend', 'frontend']);
    expect(tagIdsByEntry.get('backend-frontend-foundation')).toEqual([
      'backend',
      'frontend',
      'infra',
      'auth',
    ]);
    expect(tagIdsByEntry.get('matrix-admin-prototype')).toEqual(['backend', 'matrix', 'admin']);
    expect(tagIdsByEntry.get('repository-started')).toEqual(['infra', 'security']);
  });
});
