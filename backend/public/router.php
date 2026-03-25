<?php

/**
 * PHP built-in server router
 * Routes API requests to Laravel and all other requests to React's index.html
 */

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Pass API requests and Laravel entry point through Laravel
if (str_starts_with($path, '/api/') || $path === '/index.php') {
    require __DIR__ . '/index.php';
    return;
}

// Serve existing static files (JS, CSS, images, fonts, etc.)
$filePath = __DIR__ . $path;
if ($path !== '/' && file_exists($filePath) && !is_dir($filePath)) {
    return false; // Let PHP built-in server serve the file directly
}

// For all React Router paths (/dashboard, /market, /recommendations, etc.)
// serve React's index.html
$indexHtml = __DIR__ . '/index.html';
if (file_exists($indexHtml)) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($indexHtml);
} else {
    http_response_code(503);
    echo 'Application not ready';
}
