import {
  AngularNodeAppEngine,
  createNodeRequestHandler,
  isMainModule,
  writeResponseToNodeResponse,
} from '@angular/ssr/node';
import express from 'express';
import { join } from 'node:path';
import {
  buildPublicNotFoundHtml,
  buildPublicSeoApiUrl,
  normalizeOrigin,
  parsePublicSeoPath,
} from './server-seo';

const browserDistFolder = join(import.meta.dirname, '../browser');

const app = express();
const angularApp = new AngularNodeAppEngine();

app.use(
  express.static(browserDistFolder, {
    maxAge: '1y',
    index: false,
    redirect: false,
  }),
);

app.use(async (req, res, next) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    next();
    return;
  }

  const route = parsePublicSeoPath(req.path);
  if (route === null) {
    next();
    return;
  }

  try {
    const apiUrl = buildPublicSeoApiUrl(readRequiredOrigin('SSR_API_ORIGIN'), route);
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });
    await response.body?.cancel();

    if (response.status === 404 || response.status === 403) {
      res.status(404).type('html').send(buildPublicNotFoundHtml(readPublicOrigin(), route));
      return;
    }

    if (!response.ok) {
      next(new Error(`Public SEO preflight failed with HTTP ${response.status}.`));
      return;
    }

    next();
  } catch (error) {
    next(error);
  }
});

app.use((req, res, next) => {
  angularApp
    .handle(req)
    .then((response) => (response ? writeResponseToNodeResponse(response, res) : next()))
    .catch(next);
});

if (isMainModule(import.meta.url) || process.env['pm_id']) {
  const port = readRequiredPort();
  app.listen(port, () => {
    console.log(`Node Express server listening on http://localhost:${port}`);
  });
}

export const reqHandler = createNodeRequestHandler(app);

function readRequiredPort(): number {
  const rawPort = process.env['PORT']?.trim();
  if (!rawPort) {
    throw new Error('PORT is required for Angular SSR runtime.');
  }
  const port = Number(rawPort);
  if (!Number.isInteger(port) || port <= 0) {
    throw new Error('PORT must be a positive integer.');
  }
  return port;
}

function readPublicOrigin(): string {
  const explicitOrigin = readOptionalOrigin('SSR_PUBLIC_ORIGIN');
  if (explicitOrigin) return explicitOrigin;

  const schema = readRequiredEnv('APP_URL_SCHEMA');
  const domain = readRequiredEnv('APP_DOMAIN');
  return normalizeOrigin(`${schema}://${domain}`, 'public origin');
}

function readRequiredOrigin(name: string): string {
  return normalizeOrigin(readRequiredEnv(name), name);
}

function readOptionalOrigin(name: string): string | null {
  const value = process.env[name]?.trim();
  if (!value) return null;
  return normalizeOrigin(value, name);
}

function readRequiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`${name} is required for Angular SSR runtime.`);
  }
  return value;
}
