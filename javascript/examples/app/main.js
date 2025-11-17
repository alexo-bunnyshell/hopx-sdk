#!/usr/bin/env node
/**
 * Simple web app for template building example
 */

const http = require('http');

const PORT = process.env.PORT || 8000;

const server = http.createServer((req, res) => {
  if (req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end('Hello from Hopx template!');
  } else {
    res.writeHead(405);
    res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});
