import http from 'node:http';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(scriptDir, '..');
const serverEntry = pathToFileURL(
  resolve(frontendRoot, 'dist/my-site-frontend/server/server.mjs'),
).href;
const requests = [];

const noteDto = {
  id: '00000000-0000-0000-0000-000000000001',
  title: 'Typed notes',
  slug: 'typed-notes',
  folder: 'Engineering',
  authorUsername: 'admin',
  publishedAt: '2026-01-02T03:04:05+00:00',
  publishStatus: 'Published',
  updatedAt: '2026-01-03T03:04:05+00:00',
  excerpt: 'Fallback excerpt',
  metadata: {
    seoTitleRu: 'SEO Typed notes RU',
    seoTitleEn: 'SEO Typed notes EN',
    seoDescriptionRu:
      'SEO description RU with enough text to be useful for search snippets and social cards.',
    seoDescriptionEn:
      'SEO description EN with enough text to be useful for search snippets and social cards.',
    coverImageUrl: 'https://example.com/cover.jpg',
    coverImageAltRu: 'Typed notes cover RU',
    coverImageAltEn: 'Typed notes cover',
  },
  tags: [
    {
      id: 1,
      name: 'Angular',
      slug: 'angular',
      deletedAt: null,
      translations: {
        ru: { name: 'Angular' },
        en: { name: 'Angular' },
      },
    },
  ],
  content:
    '## Rendered SSR article body\n\nRead [[matrix:how-to-write-function|matrix question]].',
  createdAt: '2026-01-01T03:04:05+00:00',
  translations: {
    ru: {
      title: 'Typed notes',
      content:
        '## Rendered SSR article body\n\nRead [[matrix:how-to-write-function|matrix question]].',
      folder: 'Engineering',
    },
    en: {
      title: 'Typed notes EN',
      content: '## Rendered SSR article body EN',
      folder: 'Engineering',
    },
  },
};

const matrixQuestionDto = {
  id: 1,
  slug: 'how-to-write-function',
  question: 'Как написать функцию?',
  answer:
    '## Rendered SSR matrix answer\n\nФункция должна быть маленькой и проверяемой. См. [[notes:typed-notes|typed note]].',
  interviewExpectedAnswer: 'Покажите сигнатуру, ветвление и тест.',
  sheetKey: 'python',
  sheet: 'Python',
  grade: 'Junior',
  section: 'Основы',
  subsection: 'Функции',
  publishStatus: 'Published',
  translations: {
    ru: {
      question: 'Как написать функцию?',
      answer:
        '## Rendered SSR matrix answer\n\nФункция должна быть маленькой и проверяемой. См. [[notes:typed-notes|typed note]].',
      interviewExpectedAnswer: 'Покажите сигнатуру, ветвление и тест.',
      sheet: 'Python',
      section: 'Основы',
      subsection: 'Функции',
    },
    en: {
      question: 'How to write a function?',
      answer: '## Rendered SSR matrix answer\n\nA function should be small and testable.',
      interviewExpectedAnswer: 'Show a signature, a branch, and a test.',
      sheet: 'Python',
      section: 'Basics',
      subsection: 'Functions',
    },
  },
  resources: [],
};

let failure = null;
const backend = http.createServer((req, res) => {
  const url = new URL(req.url ?? '/', 'http://backend.local');
  requests.push(`${req.method ?? 'GET'} ${url.pathname}${url.search}`);
  res.setHeader('Content-Type', 'application/json');

  if (url.pathname === '/api/i18n/languages') {
    writeJson(res, {
      defaultLanguage: 'ru',
      languages: [
        { code: 'ru', label: 'Russian' },
        { code: 'en', label: 'English' },
      ],
    });
    return;
  }

  if (url.pathname === '/api/i18n/bundles/ru') {
    writeJson(res, {
      language: 'ru',
      messages: {
        'app.siteName': 'My site',
        'shell.nav.about': 'About',
        'shell.nav.matrix': 'Matrix',
        'shell.nav.notes': 'Notes',
        'shell.nav.toggleNavigation': 'Toggle navigation',
        'shell.theme.dark': 'Dark',
        'shell.theme.light': 'Light',
        'shell.theme.toggle': 'Theme',
        'shell.language.label': 'Language',
        'shell.auth.login': 'Login',
        'shell.footer.sourceCode': 'Source code',
        'shell.footer.githubProfile': 'GitHub',
        'shell.footer.telegramProfile': 'Telegram',
        'shell.footer.linkedinProfile': 'LinkedIn',
        'notes.views': '{count} views',
        'matrix.detail.question': 'Question:',
        'matrix.detail.answer': 'Answer:',
        'matrix.detail.expectedAnswer': 'Expected interview answer:',
        'matrix.detail.resources': 'External resources:',
        'shared.back': 'Back',
        'shared.edit': 'Edit',
      },
    });
    return;
  }

  if (url.pathname === '/api/notes/detail/typed-notes') {
    writeJson(res, noteDto);
    return;
  }

  if (url.pathname === '/api/notes/public-stats') {
    writeJson(res, {
      stats: [
        {
          noteId: noteDto.id,
          viewCount: 7,
          reactionCounts: {
            heart: 1,
            fire: 0,
            thinking: 0,
            neutral: 0,
            poop: 0,
          },
        },
      ],
    });
    return;
  }

  if (url.pathname === '/api/notes/tags') {
    writeJson(res, { tags: noteDto.tags });
    return;
  }

  if (url.pathname === '/api/notes/tree') {
    writeJson(res, {
      folders: [
        {
          folder: 'Engineering',
          notes: [
            {
              title: 'Typed notes',
              slug: 'typed-notes',
              publishStatus: 'Published',
              publishedAt: noteDto.publishedAt,
              updatedAt: noteDto.updatedAt,
            },
          ],
        },
      ],
    });
    return;
  }

  if (url.pathname === '/api/competency-matrix/items/public/how-to-write-function') {
    writeJson(res, matrixQuestionDto);
    return;
  }

  res.statusCode = 404;
  writeJson(res, { code: 'not_found', type: 'not_found', message: url.pathname });
});

const frontend = http.createServer(async (req, res) => {
  try {
    const { reqHandler } = await serverHandler;
    reqHandler(req, res, (error) => {
      res.statusCode = error ? 500 : 404;
      res.end(error ? String(error) : 'Not found');
    });
  } catch (error) {
    res.statusCode = 500;
    res.end(String(error));
  }
});

await listen(backend);
const backendPort = backend.address().port;
process.env.SSR_API_ORIGIN = `http://127.0.0.1:${backendPort}`;
process.env.APP_URL_SCHEMA = 'http';
process.env.APP_DOMAIN = '127.0.0.1';
process.env.NG_ALLOWED_HOSTS = '127.0.0.1';

const serverHandler = import(serverEntry);
await listen(frontend);
const frontendPort = frontend.address().port;
process.env.SSR_PUBLIC_ORIGIN = `http://127.0.0.1:${frontendPort}`;

try {
  await assertPublishedArticleHtml(frontendPort);
  await assertMissingArticleNoindex(frontendPort);
  await assertPublishedMatrixQuestionHtml(frontendPort);
  await assertMissingMatrixQuestionNoindex(frontendPort);
  console.log(`SSR smoke passed with ${requests.length} backend requests.`);
  console.log(requests.join('\n'));
} catch (error) {
  failure = error;
  console.error(error instanceof Error ? error.message : String(error));
} finally {
  await Promise.all([closeServer(frontend), closeServer(backend)]);
}

if (failure !== null) {
  process.exitCode = 1;
}

async function assertPublishedArticleHtml(frontendPort) {
  const response = await fetch(`http://127.0.0.1:${frontendPort}/ru/notes/typed-notes`);
  const html = await response.text();
  const expected = [
    ['status 200', response.status === 200],
    ['article title', html.includes('SEO Typed notes RU - My site')],
    ['article body', html.includes('Rendered SSR article body')],
    ['canonical', html.includes(`href="http://127.0.0.1:${frontendPort}/ru/notes/typed-notes"`)],
    ['hreflang ru', html.includes('hreflang="ru"')],
    ['hreflang en', html.includes('hreflang="en"')],
    ['og type article', html.includes('property="og:type" content="article"')],
    ['og image', html.includes('property="og:image" content="https://example.com/cover.jpg"')],
    ['json-ld', html.includes('"@type":"BlogPosting"')],
    ['json-ld headline', html.includes('"headline":"SEO Typed notes RU"')],
    [
      'wiki link to matrix localized',
      html.includes('href="/ru/competency-matrix/questions/how-to-write-function"'),
    ],
    ['no noindex on published article', !html.includes('name="robots" content="noindex')],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'published article SSR');
}

async function assertPublishedMatrixQuestionHtml(frontendPort) {
  const response = await fetch(
    `http://127.0.0.1:${frontendPort}/ru/competency-matrix/questions/how-to-write-function`,
  );
  const html = await response.text();
  const expected = [
    ['status 200', response.status === 200],
    ['matrix question title', html.includes('Как написать функцию? - My site')],
    ['matrix question body', html.includes('Rendered SSR matrix answer')],
    [
      'canonical',
      html.includes(
        `href="http://127.0.0.1:${frontendPort}/ru/competency-matrix/questions/how-to-write-function"`,
      ),
    ],
    ['hreflang ru', html.includes('hreflang="ru"')],
    ['hreflang en', html.includes('hreflang="en"')],
    ['json-ld faq', html.includes('"@type":"FAQPage"')],
    ['json-ld question', html.includes('"name":"Как написать функцию?"')],
    ['wiki link to note localized', html.includes('href="/ru/notes/typed-notes"')],
    ['no noindex on published matrix question', !html.includes('name="robots" content="noindex')],
    [
      'matrix public detail preflight',
      hasRequest('/api/competency-matrix/items/public/how-to-write-function', 'language=ru'),
    ],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'published matrix question SSR');
}

async function assertMissingArticleNoindex(frontendPort) {
  const response = await fetch(`http://127.0.0.1:${frontendPort}/ru/notes/missing-note`);
  const html = await response.text();
  const expected = [
    ['status 404', response.status === 404],
    ['noindex', html.includes('<meta name="robots" content="noindex, follow">')],
    [
      'canonical',
      html.includes(`href="http://127.0.0.1:${frontendPort}/ru/notes/missing-note"`),
    ],
    ['missing detail preflight', hasRequest('/api/notes/detail/missing-note', 'language=ru')],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'missing article SSR');
}

async function assertMissingMatrixQuestionNoindex(frontendPort) {
  const response = await fetch(
    `http://127.0.0.1:${frontendPort}/ru/competency-matrix/questions/missing-question`,
  );
  const html = await response.text();
  const expected = [
    ['status 404', response.status === 404],
    ['noindex', html.includes('<meta name="robots" content="noindex, follow">')],
    [
      'canonical',
      html.includes(
        `href="http://127.0.0.1:${frontendPort}/ru/competency-matrix/questions/missing-question"`,
      ),
    ],
    [
      'missing matrix preflight',
      hasRequest('/api/competency-matrix/items/public/missing-question', 'language=ru'),
    ],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'missing matrix question SSR');
}

function hasRequest(pathname, searchPart) {
  return requests.some((entry) => entry.includes(pathname) && entry.includes(searchPart));
}

function assertExpected(expected, html, label) {
  const failures = expected.filter(([, ok]) => !ok).map(([name]) => name);
  if (failures.length > 0) {
    console.error(html.slice(0, 4000));
    throw new Error(`SSR smoke failed for ${label}: ${failures.join(', ')}`);
  }
}

function writeJson(res, body) {
  res.end(JSON.stringify(body));
}

function listen(server) {
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', resolve);
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    server.close(resolve);
  });
}
