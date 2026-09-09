import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '..');
const frontendDir = join(rootDir, 'frontend');

const host = process.env.HOST || '127.0.0.1';
const port = Number(process.env.PORT || 3000);
const backendPort = Number(process.env.BACKEND_PORT || 8000);

const mimeTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.ico', 'image/x-icon'],
]);

const server = createServer(async (request, response) => {
  try {
    const { pathname } = new URL(request.url, `http://${host}:${port}`);
    response.setHeader('X-Content-Type-Options', 'nosniff');

    // Proxy /v1/* and /api/* to FastAPI backend
    if (pathname.startsWith('/v1/') || pathname.startsWith('/api/')) {
      const targetUrl = new URL(request.url, `http://127.0.0.1:${backendPort}`);
      const proxyReq = (await import('node:http')).request(
        targetUrl,
        {
          method: request.method,
          headers: { ...request.headers, host: `127.0.0.1:${backendPort}` },
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

    // Resolve file from frontend directory
    let relativePath = pathname === '/' ? 'index.html' : pathname.replace(/^\//, '');
    let filePath = join(frontendDir, relativePath);

    if (!existsSync(filePath)) {
      // Fallback for SPA routing to index.html if no extension
      if (!relativePath.includes('.')) {
        filePath = join(frontendDir, 'index.html');
      } else {
        response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        response.end(request.method === 'HEAD' ? undefined : 'Not found');
        return;
      }
    }

    const ext = '.' + filePath.split('.').pop();
    const contentType = mimeTypes.get(ext) || 'application/octet-stream';
    const content = await readFile(filePath);

    response.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'no-cache' });
    response.end(request.method === 'HEAD' ? undefined : content);
  } catch (error) {
    console.error('Server error:', error);
    response.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Internal server error');
  }
});

server.on('error', (error) => {
  console.error(`Could not start server: ${error.message}`);
  process.exit(1);
});

server.listen(port, host, () => {
  console.log(`Recollect Preview Server running at http://${host}:${server.address().port}`);
  console.log(`Proxying backend requests to http://127.0.0.1:${backendPort}`);
});
