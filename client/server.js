const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const buildDir = path.join(__dirname, 'build');

// Proxy /api/* to Laravel backend
app.use(
  '/api',
  createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    secure: false,
    onError: (err, req, res) => {
      console.error('Backend proxy error:', err.message);
      res.status(502).json({ success: false, error: 'Backend unavailable' });
    },
  })
);

// Serve React static build
app.use(express.static(buildDir));

app.get('*', (req, res) => {
  res.sendFile(path.join(buildDir, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend server on port ${PORT} → API: ${BACKEND_URL}`);
});
