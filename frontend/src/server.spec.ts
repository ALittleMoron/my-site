import { createServer, get } from 'node:http';
import { AddressInfo } from 'node:net';
import { AngularSsrEngine, AngularSsrResponseWriter, createExpressApp } from './server-app';

describe('SSR Express server', () => {
  const requiredEnvNames = [
    'PORT',
    'SSR_API_ORIGIN',
    'SSR_PUBLIC_ORIGIN',
    'APP_URL_SCHEMA',
    'APP_DOMAIN',
  ];
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    for (const name of requiredEnvNames) {
      delete process.env[name];
    }
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('serves healthz without reading SSR environment or calling Angular', async () => {
    const angularApp: AngularSsrEngine = {
      handle: jest.fn().mockRejectedValue(new Error('Angular should not handle healthz')),
    };
    const responseWriter: AngularSsrResponseWriter = jest.fn();
    const app = createExpressApp({
      browserDistFolder: '/tmp/non-existent-browser-dist',
      angularApp,
      responseWriter,
    });
    const server = createServer(app);

    try {
      await new Promise<void>((resolve) => {
        server.listen(0, '127.0.0.1', resolve);
      });
      const address = server.address() as AddressInfo;
      const response = await request(`http://127.0.0.1:${address.port}/healthz`);

      expect(response.status).toBe(200);
      expect(response.body).toBe('');
      expect(angularApp.handle).not.toHaveBeenCalled();
      expect(responseWriter).not.toHaveBeenCalled();
    } finally {
      await new Promise<void>((resolve, reject) => {
        server.close((error) => {
          if (error) {
            reject(error);
            return;
          }
          resolve();
        });
      });
    }
  });
});

interface HttpResponse {
  readonly status: number | undefined;
  readonly body: string;
}

function request(url: string): Promise<HttpResponse> {
  return new Promise((resolve, reject) => {
    get(url, (response) => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', (chunk: string) => {
        body += chunk;
      });
      response.on('end', () => {
        resolve({ status: response.statusCode, body });
      });
    }).on('error', reject);
  });
}
