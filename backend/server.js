/**
 * Telangana Tourism Dashboard — backend API
 * ------------------------------------------------------------
 * Plain Node.js (no npm dependencies). Serves:
 *   - JSON REST API under /api/*
 *   - the static frontend from ../public
 *
 * Run with:  node server.js
 * Then open: http://localhost:3000
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, '..', 'public');

const trends = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'trends.json'), 'utf8'));
const places = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'places.json'), 'utf8'));

const MIME = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'text/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2'
};

function sendJson(res, statusCode, data) {
  const body = JSON.stringify(data);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=UTF-8',
    'Content-Length': Buffer.byteLength(body),
    'Access-Control-Allow-Origin': '*'
  });
  res.end(body);
}

// ---------- API handlers ----------

function getOverview() {
  const y24 = trends['2024'].totals;
  const y25 = trends['2025'].totals;

  const totalTourists = y24.total + y25.total;
  const totalDomestic = y24.domestic + y25.domestic;
  const totalForeign = y24.foreign + y25.foreign;
  const totalRevenueLakhs = +(y24.revenueLakhs + y25.revenueLakhs).toFixed(2);
  const yoyGrowthPct = +(((y25.total - y24.total) / y24.total) * 100).toFixed(2);

  const topCircuit = [...places].sort((a, b) => b.totalFootfall - a.totalFootfall)[0];

  return {
    totalTourists,
    totalDomestic,
    totalForeign,
    totalRevenueLakhs,
    yoyGrowthPct,
    year2024: y24,
    year2025: y25,
    topCircuit: { id: topCircuit.id, name: topCircuit.name, footfall: topCircuit.totalFootfall },
    circuitCount: places.length
  };
}

function handleApi(req, res, pathname) {
  if (pathname === '/api/overview' && req.method === 'GET') {
    return sendJson(res, 200, getOverview());
  }
  if (pathname === '/api/trends' && req.method === 'GET') {
    return sendJson(res, 200, trends);
  }
  if (pathname === '/api/places' && req.method === 'GET') {
    return sendJson(res, 200, [...places].sort((a, b) => a.rank - b.rank));
  }
  const placeMatch = pathname.match(/^\/api\/places\/([a-z0-9-]+)$/i);
  if (placeMatch && req.method === 'GET') {
    const place = places.find((p) => p.id === placeMatch[1]);
    if (!place) return sendJson(res, 404, { error: 'Place not found' });
    return sendJson(res, 200, place);
  }
  return sendJson(res, 404, { error: 'Unknown API route' });
}

// ---------- Static file serving ----------

function serveStatic(req, res, pathname) {
  let relativePath = pathname === '/' ? '/index.html' : pathname;
  const resolved = path.normalize(path.join(PUBLIC_DIR, relativePath));

  // Prevent path traversal outside the public directory
  if (!resolved.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.readFile(resolved, (err, data) => {
    if (err) {
      // SPA-friendly fallback: unknown paths serve index.html
      if (path.extname(resolved) === '') {
        return fs.readFile(path.join(PUBLIC_DIR, 'index.html'), (err2, indexData) => {
          if (err2) {
            res.writeHead(404);
            return res.end('Not found');
          }
          res.writeHead(200, { 'Content-Type': MIME['.html'] });
          res.end(indexData);
        });
      }
      res.writeHead(404);
      return res.end('Not found');
    }
    const ext = path.extname(resolved).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

// ---------- Server ----------

const server = http.createServer((req, res) => {
  const { pathname } = new URL(req.url, `http://${req.headers.host || 'localhost'}`);

  if (pathname.startsWith('/api/')) {
    return handleApi(req, res, pathname);
  }
  return serveStatic(req, res, pathname);
});

server.listen(PORT, () => {
  console.log(`Telangana Tourism Dashboard running at http://localhost:${PORT}`);
});
