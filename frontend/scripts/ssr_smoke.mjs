import { startSsrFixture } from './ssr_mock_app.mjs';

let failure = null;
const fixture = await startSsrFixture();
const { frontendPort, requests } = fixture;

try {
  await assertSiteBuildCaseStudyHtml(frontendPort, requests);
  await assertPublishedArticleHtml(frontendPort, requests);
  await assertMissingArticleNoindex(frontendPort, requests);
  await assertPublishedMatrixQuestionHtml(frontendPort, requests);
  await assertMissingMatrixQuestionNoindex(frontendPort, requests);
  console.log(`SSR smoke passed with ${requests.length} backend requests.`);
  console.log(requests.join('\n'));
} catch (error) {
  failure = error;
  console.error(error instanceof Error ? error.message : String(error));
} finally {
  await fixture.close();
}

if (failure !== null) {
  process.exitCode = 1;
}

async function assertSiteBuildCaseStudyHtml(frontendPort, requests) {
  const response = await fetch(`http://127.0.0.1:${frontendPort}/ru/how-this-site-is-built`);
  const html = await response.text();
  const expected = [
    ['status 200', response.status === 200],
    ['title', html.includes('How this site is built - My site')],
    ['hero', html.includes('Portfolio case study about a production-minded personal site.')],
    ['architecture', html.includes('Angular hybrid SSR/CSR and backend-driven i18n.')],
    ['source code CTA', html.includes('href="https://github.com/ALittleMoron/my-site"')],
    [
      'canonical',
      html.includes(`href="http://127.0.0.1:${frontendPort}/ru/how-this-site-is-built"`),
    ],
    ['hreflang ru', html.includes('hreflang="ru"')],
    ['hreflang en', html.includes('hreflang="en"')],
    ['no API request beyond i18n', requests.every((entry) => !entry.includes('/api/notes/'))],
    ['no noindex on case study', !html.includes('name="robots" content="noindex')],
  ];
  assertExpected(expected, html, 'site-build case study SSR');
}

async function assertPublishedArticleHtml(frontendPort, requests) {
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

async function assertPublishedMatrixQuestionHtml(frontendPort, requests) {
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
      hasRequest(requests, '/api/competency-matrix/items/public/how-to-write-function', 'language=ru'),
    ],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'published matrix question SSR');
}

async function assertMissingArticleNoindex(frontendPort, requests) {
  const response = await fetch(`http://127.0.0.1:${frontendPort}/ru/notes/missing-note`);
  const html = await response.text();
  const expected = [
    ['status 404', response.status === 404],
    ['noindex', html.includes('<meta name="robots" content="noindex, follow">')],
    [
      'canonical',
      html.includes(`href="http://127.0.0.1:${frontendPort}/ru/notes/missing-note"`),
    ],
    ['missing detail preflight', hasRequest(requests, '/api/notes/detail/missing-note', 'language=ru')],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'missing article SSR');
}

async function assertMissingMatrixQuestionNoindex(frontendPort, requests) {
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
      hasRequest(requests, '/api/competency-matrix/items/public/missing-question', 'language=ru'),
    ],
    ['no analytics request', requests.every((entry) => !entry.includes('/analytics/'))],
    ['no reaction request', requests.every((entry) => !entry.includes('/reaction'))],
  ];
  assertExpected(expected, html, 'missing matrix question SSR');
}

function hasRequest(requests, pathname, searchPart) {
  return requests.some((entry) => entry.includes(pathname) && entry.includes(searchPart));
}

function assertExpected(expected, html, label) {
  const failures = expected.filter(([, ok]) => !ok).map(([name]) => name);
  if (failures.length > 0) {
    console.error(html.slice(0, 4000));
    throw new Error(`SSR smoke failed for ${label}: ${failures.join(', ')}`);
  }
}
