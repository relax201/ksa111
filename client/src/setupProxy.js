const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all /api/v1/* requests to Laravel backend on port 8000
  app.use(
    '/api',
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      onError: (err, req, res) => {
        console.error('API Proxy Error:', err.message);
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: false,
          error: 'Backend unavailable: ' + err.message
        }));
      }
    })
  );
};
