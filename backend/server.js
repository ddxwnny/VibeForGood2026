import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3000);
const assets = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
]);

const server = createServer(async (request, response) => {
  try {
    const { pathname } = new URL(request.url, 'http://localhost');
    response.setHeader('X-Content-Type-Options', 'nosniff');
    if (pathname.startsWith('/v1/')) {
      const targetUrl = new URL(request.url, 'http://127.0.0.1:8000');
      const proxyReq = (await import('node:http')).request(
        targetUrl,
        {
          method: request.method,
          headers: { ...request.headers, host: '127.0.0.1:8000' },
        },
        (proxyRes) => {
          response.writeHead(proxyRes.statusCode, proxyRes.headers);
          proxyRes.pipe(response, { end: true });
        }
      );
      proxyReq.on('error', (err) => {
        response.writeHead(502, { 'Content-Type': 'application/json' });
        response.end(JSON.stringify({ error: 'Backend unreachable', detail: err.message }));
      });
      request.pipe(proxyReq, { end: true });
      return;
    }

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      response.writeHead(405, { Allow: 'GET, HEAD' });
      response.end();
      return;
    }
    if (pathname === '/api/health') {
      response.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store',
      });
      response.end(request.method === 'HEAD' ? undefined : JSON.stringify({
        status: 'ok',
        message: 'Your frontend is connected to the backend.',
      }));
      return;
    }
    const asset = assets.get(pathname);
    if (!asset) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end(request.method === 'HEAD' ? undefined : 'Not found');
      return;
    }
    const [filename, contentType] = asset;
    const content = await readFile(new URL(`../frontend/${filename}`, import.meta.url));
    response.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'no-cache' });
    response.end(request.method === 'HEAD' ? undefined : content);
  } catch (error) {
    console.error(error);
    response.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Internal server error');
  }
});

server.on('error', (error) => {
  console.error(`Could not start server: ${error.message}`);
  process.exit(1);
});
server.listen(port, host, () => {
  console.log(`VibeForGood2026 is running at http://${host}:${server.address().port}`);
});
