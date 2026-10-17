import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.SKILL_PREVIEW_PORT || 4311);
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.png': 'image/png' };
http.createServer((request, response) => {
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname); }
  catch { response.writeHead(400).end('Invalid URL'); return; }
  const destination = path.resolve(root, `.${pathname === '/' ? '/index.html' : pathname}`);
  if (!destination.startsWith(`${root}${path.sep}`)) { response.writeHead(403).end('Forbidden'); return; }
  fs.stat(destination, (error, stat) => {
    if (error || !stat.isFile()) { response.writeHead(404).end('Not found'); return; }
    response.writeHead(200, { 'Content-Type': mime[path.extname(destination)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    fs.createReadStream(destination).pipe(response);
  });
}).listen(port, '127.0.0.1', () => console.log(`Skill preview: http://127.0.0.1:${port}/`));
