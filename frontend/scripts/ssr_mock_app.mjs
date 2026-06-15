import http from 'node:http';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { gzipSync } from 'node:zlib';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const frontendRoot = resolve(scriptDir, '..');
const defaultServerEntry = pathToFileURL(
  resolve(frontendRoot, 'dist/my-site-frontend/server/server.mjs'),
).href;

export const noteDto = {
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

export const matrixQuestionDto = {
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

export async function startSsrFixture(options = {}) {
  const frontendPortOption = options.frontendPort ?? 0;
  const requests = [];
  const backend = createMockBackend(requests);

  await listen(backend, options.backendPort ?? 0);
  const backendPort = backend.address().port;
  process.env.SSR_API_ORIGIN = `http://127.0.0.1:${backendPort}`;
  process.env.APP_URL_SCHEMA = 'http';
  process.env.APP_DOMAIN = '127.0.0.1';
  process.env.NG_ALLOWED_HOSTS = '127.0.0.1';

  const serverHandler = import(options.serverEntry ?? defaultServerEntry);
  const frontend = createFrontendServer(serverHandler);
  await listen(frontend, frontendPortOption);
  const frontendPort = frontend.address().port;
  process.env.SSR_PUBLIC_ORIGIN = `http://127.0.0.1:${frontendPort}`;

  return {
    backend,
    frontend,
    backendPort,
    frontendPort,
    requests,
    async close() {
      await Promise.all([closeServer(frontend), closeServer(backend)]);
    },
  };
}

function createFrontendServer(serverHandler) {
  return http.createServer(async (req, res) => {
    installGzipForTextResponses(req, res);

    try {
      const url = new URL(req.url ?? '/', 'http://frontend.local');
      if ((req.method === 'GET' || req.method === 'HEAD') && url.pathname === '/robots.txt') {
        writeText(res, 'text/plain; charset=utf-8', buildRobotsTxt(readFixtureOrigin(req)));
        return;
      }

      if ((req.method === 'GET' || req.method === 'HEAD') && url.pathname === '/sitemap.xml') {
        writeText(res, 'application/xml; charset=utf-8', buildSitemapXml(readFixtureOrigin(req)));
        return;
      }

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
}

function installGzipForTextResponses(req, res) {
  const originalWriteHead = res.writeHead.bind(res);
  const originalEnd = res.end.bind(res);
  const chunks = [];

  res.writeHead = (...args) => {
    applyWriteHeadArgs(res, args);
    return res;
  };

  res.write = (chunk, encoding, callback) => {
    const normalized = normalizeWriteArgs(chunk, encoding, callback);
    if (normalized.chunk !== undefined) {
      chunks.push(toBuffer(normalized.chunk, normalized.encoding));
    }
    normalized.callback?.();
    return true;
  };

  res.end = (chunk, encoding, callback) => {
    const normalized = normalizeWriteArgs(chunk, encoding, callback);
    if (normalized.chunk !== undefined) {
      chunks.push(toBuffer(normalized.chunk, normalized.encoding));
    }

    const body = Buffer.concat(chunks);
    if (!shouldGzipResponse(req, res, body)) {
      res.writeHead = originalWriteHead;
      return originalEnd(body, normalized.callback);
    }

    const gzippedBody = gzipSync(body);
    res.setHeader('Content-Encoding', 'gzip');
    res.setHeader('Vary', appendVaryAcceptEncoding(res.getHeader('Vary')));
    res.setHeader('Content-Length', String(gzippedBody.length));
    res.writeHead = originalWriteHead;
    return originalEnd(gzippedBody, normalized.callback);
  };
}

function applyWriteHeadArgs(res, args) {
  const [statusCode, statusMessageOrHeaders, maybeHeaders] = args;
  if (Number.isInteger(statusCode)) {
    res.statusCode = statusCode;
  }

  const headers =
    typeof statusMessageOrHeaders === 'string' ? maybeHeaders : statusMessageOrHeaders;
  if (typeof statusMessageOrHeaders === 'string') {
    res.statusMessage = statusMessageOrHeaders;
  }
  if (headers === undefined) return;

  if (Array.isArray(headers)) {
    for (let index = 0; index < headers.length; index += 2) {
      res.setHeader(headers[index], headers[index + 1]);
    }
    return;
  }

  for (const [name, value] of Object.entries(headers)) {
    res.setHeader(name, value);
  }
}

function normalizeWriteArgs(chunk, encoding, callback) {
  if (typeof chunk === 'function') {
    return { chunk: undefined, encoding: undefined, callback: chunk };
  }
  if (typeof encoding === 'function') {
    return { chunk, encoding: undefined, callback: encoding };
  }
  return { chunk, encoding, callback };
}

function toBuffer(chunk, encoding) {
  if (Buffer.isBuffer(chunk)) return chunk;
  if (chunk instanceof Uint8Array) return Buffer.from(chunk);
  return Buffer.from(String(chunk), encoding);
}

function shouldGzipResponse(req, res, body) {
  const acceptEncoding = String(req.headers['accept-encoding'] ?? '');
  const contentType = String(res.getHeader('Content-Type') ?? '').toLowerCase();
  return (
    body.length > 0 &&
    acceptEncoding.includes('gzip') &&
    !res.hasHeader('Content-Encoding') &&
    res.statusCode !== 204 &&
    res.statusCode !== 304 &&
    isCompressibleContentType(contentType)
  );
}

function isCompressibleContentType(contentType) {
  return (
    contentType.startsWith('text/') ||
    contentType.includes('javascript') ||
    contentType.includes('json') ||
    contentType.includes('xml') ||
    contentType.includes('svg')
  );
}

function appendVaryAcceptEncoding(value) {
  if (value === undefined) return 'Accept-Encoding';
  const current = Array.isArray(value) ? value.join(', ') : String(value);
  return current
    .split(',')
    .map((part) => part.trim().toLowerCase())
    .includes('accept-encoding')
    ? current
    : `${current}, Accept-Encoding`;
}

function readFixtureOrigin(req) {
  const explicitOrigin = process.env.SSR_PUBLIC_ORIGIN?.trim();
  if (explicitOrigin) return explicitOrigin;

  const host = req.headers.host ?? '127.0.0.1';
  return `http://${host}`;
}

function buildRobotsTxt(origin) {
  return (
    'User-agent: *\n'
    + 'Allow: /ru/\n'
    + 'Allow: /en/\n'
    + 'Allow: /sitemap.xml\n'
    + 'Disallow: /api/\n'
    + 'Disallow: /login\n'
    + 'Disallow: /about-me\n'
    + 'Disallow: /how-this-site-is-built\n'
    + 'Disallow: /notes\n'
    + 'Disallow: /competency-matrix\n'
    + 'Disallow: /sitemap\n'
    + `Sitemap: ${origin}/sitemap.xml\n`
  );
}

function buildSitemapXml(origin) {
  const urls = [
    '/ru/about-me',
    '/en/about-me',
    '/ru/how-this-site-is-built',
    '/en/how-this-site-is-built',
    '/ru/notes/typed-notes',
    '/en/notes/typed-notes',
    '/ru/competency-matrix/questions/how-to-write-function',
    '/en/competency-matrix/questions/how-to-write-function',
  ];
  const entries = urls
    .map((path) => `  <url>\n    <loc>${origin}${path}</loc>\n  </url>`)
    .join('\n');
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + `${entries}\n`
    + '</urlset>\n'
  );
}

function writeText(res, contentType, body) {
  res.statusCode = 200;
  res.setHeader('Content-Type', contentType);
  res.end(body);
}

function createMockBackend(requests) {
  return http.createServer((req, res) => {
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

    if (url.pathname === '/api/i18n/bundles/ru' || url.pathname === '/api/i18n/bundles/en') {
      writeJson(res, {
        language: url.pathname.endsWith('/en') ? 'en' : 'ru',
        messages: buildMessages(),
      });
      return;
    }

    if (url.pathname === '/api/notes') {
      writeJson(res, {
        totalCount: 1,
        totalPages: 1,
        notes: [noteSummary()],
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

    if (url.pathname === '/api/competency-matrix/sheets') {
      writeJson(res, {
        sheets: [{ key: matrixQuestionDto.sheetKey, name: matrixQuestionDto.sheet }],
      });
      return;
    }

    if (url.pathname === '/api/competency-matrix/items') {
      writeJson(res, {
        sheetKey: matrixQuestionDto.sheetKey,
        sheet: matrixQuestionDto.sheet,
        sections: [
          {
            section: matrixQuestionDto.section,
            subsections: [
              {
                subsection: matrixQuestionDto.subsection,
                grades: [
                  {
                    grade: matrixQuestionDto.grade,
                    items: [
                      {
                        id: matrixQuestionDto.id,
                        slug: matrixQuestionDto.slug,
                        question: matrixQuestionDto.question,
                      },
                    ],
                  },
                ],
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
}

function noteSummary() {
  return {
    id: noteDto.id,
    title: noteDto.title,
    slug: noteDto.slug,
    folder: noteDto.folder,
    authorUsername: noteDto.authorUsername,
    publishedAt: noteDto.publishedAt,
    publishStatus: noteDto.publishStatus,
    updatedAt: noteDto.updatedAt,
    excerpt: noteDto.excerpt,
    metadata: noteDto.metadata,
    tags: noteDto.tags,
  };
}

function buildMessages() {
  return {
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
    'shell.footer.siteBuild': 'How this site is built',
    'shell.footer.githubProfile': 'GitHub',
    'shell.footer.telegramProfile': 'Telegram',
    'shell.footer.linkedinProfile': 'LinkedIn',
    'siteBuild.seo.title': 'How this site is built',
    'siteBuild.seo.description': 'A portfolio case study about this site.',
    'siteBuild.hero.kicker': 'Case study',
    'siteBuild.hero.title': 'How this site is built',
    'siteBuild.hero.lead': 'Portfolio case study about a production-minded personal site.',
    'siteBuild.hero.sourceCode': 'Source code',
    'siteBuild.hero.matrixLink': 'Open matrix',
    'siteBuild.hero.logoAlt': 'Site logo',
    'siteBuild.problem.title': 'Problem',
    'siteBuild.problem.body': 'Portfolio, notes, and competency matrix in one product.',
    'siteBuild.architecture.title': 'Architecture',
    'siteBuild.architecture.backendTitle': 'Backend',
    'siteBuild.architecture.backendBody': 'Litestar, SQLAlchemy, Dishka, and PostgreSQL.',
    'siteBuild.architecture.frontendTitle': 'Frontend',
    'siteBuild.architecture.frontendBody': 'Angular hybrid SSR/CSR and backend-driven i18n.',
    'siteBuild.architecture.infraTitle': 'Infrastructure',
    'siteBuild.architecture.infraBody': 'nginx, Docker, MinIO, Valkey, and TaskIQ.',
    'siteBuild.decisions.title': 'Engineering decisions',
    'siteBuild.decision.cleanArchitecture': 'Clean Architecture',
    'siteBuild.decision.localizedContent': 'RU/EN localization',
    'siteBuild.decision.privacyAnalytics': 'Privacy-safe analytics',
    'siteBuild.quality.title': 'Quality and operations',
    'siteBuild.quality.body':
      'Quality checks, security gates, SSR smoke, and strict Lighthouse CI quality/performance gates.',
    'siteBuild.next.title': 'Next',
    'siteBuild.next.body': 'Feeds, roadmap, and deployment hardening.',
    'siteBuild.next.notesLink': 'Go to notes',
    'notes.title': 'Notes',
    'notes.views': '{count} views',
    'notes.filters.search': 'Search',
    'notes.filters.searchPlaceholder': 'Search notes',
    'notes.filters.from': 'From',
    'notes.filters.to': 'To',
    'notes.filters.apply': 'Apply',
    'notes.filters.reset': 'Reset',
    'notes.sidePanel.open': 'Open notes tree',
    'notes.sidePanel.close': 'Close notes tree',
    'notes.datePicker.placeholder': 'yyyy-mm-dd',
    'notes.datePicker.open': 'Open calendar',
    'notes.datePicker.previousMonth': 'Previous month',
    'notes.datePicker.nextMonth': 'Next month',
    'notes.datePicker.openMonthYearPicker': 'Choose month and year',
    'notes.datePicker.previousYear': 'Previous year',
    'notes.datePicker.nextYear': 'Next year',
    'notes.reactions': 'Reactions',
    'matrix.title': 'Competency matrix',
    'matrix.seo.title': 'Competency matrix',
    'matrix.seo.description': 'Competency matrix for Junior/Middle/Senior developers.',
    'matrix.grid.sheetsAria': 'Matrix sheets',
    'matrix.grid.section': 'Section',
    'matrix.grid.subsection': 'Subsection',
    'matrix.detail.question': 'Question:',
    'matrix.detail.answer': 'Answer:',
    'matrix.detail.expectedAnswer': 'Expected interview answer:',
    'matrix.detail.resources': 'External resources:',
    'matrix.detailAria': 'Matrix question detail',
    'matrix.empty': 'No matrix questions found.',
    'shared.back': 'Back',
    'shared.close': 'Close',
    'shared.edit': 'Edit',
    'shared.loading': 'Loading',
    'shared.retry': 'Retry',
    'shared.notSet': 'Not set',
    'enum.grade.Junior': 'Junior',
    'enum.grade.JuniorPlus': 'Junior+',
    'enum.grade.Middle': 'Middle',
    'enum.grade.MiddlePlus': 'Middle+',
    'enum.grade.Senior': 'Senior',
    'enum.noteReaction.heart': 'Heart',
    'enum.noteReaction.fire': 'Fire',
    'enum.noteReaction.thinking': 'Thinking',
    'enum.noteReaction.neutral': 'Neutral',
    'enum.noteReaction.poop': 'Poop',
  };
}

function writeJson(res, body) {
  res.end(JSON.stringify(body));
}

function listen(server, port) {
  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', resolve);
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    server.close(resolve);
  });
}
