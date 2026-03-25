<?php
/**
 * TASI3 System Runner
 * 
 * Este script ejecuta el sistema TASI3 y muestra los resultados en un formato amigable.
 */

// Definir la codificación UTF-8 para la salida
header('Content-Type: text/html; charset=utf-8');

// Función para ejecutar un comando de integración y obtener los resultados
function runIntegration($action) {
    $command = "php integration/run_integration.php {$action}";
    $output = shell_exec($command);
    return json_decode($output, true);
}

// Función para mostrar los resultados en formato HTML
function displayResults($title, $results) {
    echo "<div class='result-section'>";
    echo "<h2>{$title}</h2>";
    
    if (isset($results['success']) && $results['success']) {
        echo "<div class='success'>✅ Operación exitosa</div>";
        
        if (isset($results['data'])) {
            echo "<div class='data'>";
            echo "<pre>" . json_encode($results['data'], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "</pre>";
            echo "</div>";
        }
    } else {
        echo "<div class='error'>❌ Error: " . (isset($results['error']) ? $results['error'] : 'Error desconocido') . "</div>";
    }
    
    echo "</div>";
}

?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام تاسي3 - عرض النتائج</title>
    <style>
        body {
            font-family: 'Tajawal', Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #1976d2;
            text-align: center;
            margin-bottom: 30px;
        }
        .result-section {
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        h2 {
            color: #333;
            border-bottom: 2px solid #1976d2;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .success {
            color: #4caf50;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .error {
            color: #f44336;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .data {
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>نظام تحليل الأسهم السعودية (تاسي3)</h1>
        
        <?php
        // Ejecutar y mostrar los resultados de las diferentes funcionalidades
        displayResults("توصيات الاستثمار", runIntegration("recommend"));
        displayResults("التحليل الفني", runIntegration("technical"));
        displayResults("التحليل الأساسي", runIntegration("fundamental"));
        displayResults("بيانات السوق", runIntegration("market"));
        displayResults("البيانات المالية", runIntegration("financial"));
        displayResults("تحليل المشاعر", runIntegration("sentiment"));
        ?>
        
        <div class="footer">
            <p>© 2025 نظام تاسي3 - جميع الحقوق محفوظة</p>
        </div>
    </div>
</body>
</html>