export type PublicArticleLanguage = 'ru' | 'en';

export interface PublicArticleRoute {
  language: PublicArticleLanguage;
  slug: string;
}

const PUBLIC_ARTICLE_PATH_PATTERN = /^\/(ru|en)\/notes\/([a-z0-9]+(?:-[a-z0-9]+)*)\/?$/;

export function parsePublicArticlePath(pathname: string): PublicArticleRoute | null {
  const match = PUBLIC_ARTICLE_PATH_PATTERN.exec(pathname);
  if (!match) return null;
  return {
    language: match[1] as PublicArticleLanguage,
    slug: match[2],
  };
}

export function buildPublicArticleApiUrl(apiOrigin: string, route: PublicArticleRoute): URL {
  const url = new URL(`/api/notes/detail/${route.slug}`, apiOrigin);
  url.searchParams.set('language', route.language);
  url.searchParams.set('onlyPublished', 'true');
  return url;
}

export function buildArticleNotFoundHtml(publicOrigin: string, route: PublicArticleRoute): string {
  const canonicalUrl = new URL(`/${route.language}/notes/${route.slug}`, publicOrigin).toString();
  return `<!doctype html>
<html lang="${route.language}">
  <head>
    <meta charset="utf-8">
    <title>Article not found</title>
    <meta name="robots" content="noindex, follow">
    <link rel="canonical" href="${escapeHtml(canonicalUrl)}">
  </head>
  <body>
    <main>
      <h1>Article not found</h1>
    </main>
  </body>
</html>`;
}

export function normalizeOrigin(value: string, name: string): string {
  const origin = new URL(value).origin;
  if (origin !== value.replace(/\/$/, '')) {
    throw new Error(`${name} must be an origin without a path.`);
  }
  return origin;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
}
