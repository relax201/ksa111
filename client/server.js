const express = require('express');
const path = require('path');
const app = express();

const PORT = process.env.PORT || 3000;

// Support both: running from project root (node client/server.js)
// and running from client/ dir (node server.js)
const buildDir = path.join(__dirname, 'build');

app.use(express.static(buildDir));

app.get('*', (req, res) => {
  res.sendFile(path.join(buildDir, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Frontend server running on port ${PORT}`);
});
