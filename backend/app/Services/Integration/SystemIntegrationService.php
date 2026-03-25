<?php

namespace App\Services\Integration;

use Exception;
use Illuminate\Support\Facades\Log;

/**
 * SystemIntegrationService
 * 
 * Este servicio proporciona métodos para integrar diferentes componentes del sistema,
 * incluyendo el motor de recomendación, análisis técnico y fundamental, y la recopilación de datos.
 */
class SystemIntegrationService
{
    /**
     * Ruta al directorio de integración
     */
    protected $integrationPath;

    /**
     * Constructor
     */
    public function __construct()
    {
        $this->integrationPath = base_path('../integration');
    }

    /**
     * Ejecutar el script de integración con los parámetros proporcionados
     *
     * @param array $params Parámetros para el script de integración
     * @return array Resultado de la ejecución
     */
    protected function executeIntegration(array $params): array
    {
        try {
            // التحقق من وجود سكريبت التكامل الحقيقي
            $scriptPath = $this->integrationPath . '/system_integration.py';

            if (!file_exists($scriptPath)) {
                throw new Exception("سكريبت التكامل غير موجود: {$scriptPath}");
            }

            // تحويل المعلمات إلى JSON
            $jsonParams = json_encode($params, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception("خطأ في ترميز المعلمات: " . json_last_error_msg());
            }

            // Write params to a temp file to avoid shell escaping issues on Windows
            $tempFile = tempnam(sys_get_temp_dir(), 'tasi3_');
            file_put_contents($tempFile, $jsonParams);

            $escapedScript = escapeshellarg($scriptPath);
            $escapedTempFile = escapeshellarg($tempFile);

            // تنفيذ سكريبت Python
            $pythonExecutable = 'python3';
            $logPath = storage_path('logs/python_integration.log');
            $command = "{$pythonExecutable} {$escapedScript} {$escapedTempFile} 2>> " . escapeshellarg($logPath);

            Log::info("Executing integration: " . json_encode($params));
            $output = shell_exec($command);
            @unlink($tempFile);
            
            if ($output === null) {
                throw new Exception("Error al ejecutar el script de integración");
            }
            
            // Analizar la salida JSON
            $result = json_decode($output, true);
            
            if (json_last_error() !== JSON_ERROR_NONE) {
                throw new Exception("Error al decodificar la salida del script: " . json_last_error_msg());
            }
            
            return $result;
        } catch (Exception $e) {
            Log::error("Error de integración: " . $e->getMessage());
            
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }

    /**
     * Ejecuta el motor de recomendación y devuelve los resultados
     *
     * @param array $parameters Parámetros para el motor de recomendación
     * @return array Resultados de la recomendación
     */
    public function executeRecommendationEngine(array $parameters): array
    {
        try {
            $params = [
                'action' => 'recommend',
                'risk_profile' => $parameters['risk_profile'] ?? 'moderate',
                'investment_horizon' => $parameters['investment_horizon'] ?? 'medium',
                'sectors' => $parameters['sectors'] ?? [],
                'exclude_symbols' => $parameters['exclude_symbols'] ?? [],
                'max_results' => $parameters['max_results'] ?? 10
            ];
            
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error en el servicio de integración: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Ejecuta el análisis técnico para un símbolo específico
     *
     * @param string $symbol Símbolo de la acción
     * @param array $indicators Indicadores técnicos a calcular
     * @param string $timeframe Marco temporal (diario, semanal, etc.)
     * @return array Resultados del análisis técnico
     */
    public function executeTechnicalAnalysis(string $symbol, array $indicators, string $timeframe = 'daily'): array
    {
        try {
            $params = [
                'action' => 'technical_analysis',
                'symbol' => $symbol,
                'indicators' => $indicators,
                'timeframe' => $timeframe
            ];
            
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error en el análisis técnico: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Ejecuta el análisis fundamental para un símbolo específico
     *
     * @param string $symbol Símbolo de la acción
     * @param array $metrics Métricas fundamentales a calcular
     * @return array Resultados del análisis fundamental
     */
    public function executeFundamentalAnalysis(string $symbol, array $metrics): array
    {
        try {
            $params = [
                'action' => 'fundamental_analysis',
                'symbol' => $symbol,
                'metrics' => $metrics
            ];
            
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error en el análisis fundamental: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Recopila datos financieros actualizados
     *
     * @param array $symbols Lista de símbolos para recopilar datos
     * @param string $dataType Tipo de datos a recopilar (market, financial, sentiment)
     * @return array Resultados de la recopilación de datos
     */
    public function collectData(array $symbols, string $dataType): array
    {
        try {
            $params = [];
            
            if ($dataType === 'market') {
                $params = [
                    'action' => 'collect_market_data',
                    'symbols' => $symbols
                ];
            } elseif ($dataType === 'financial') {
                $params = [
                    'action' => 'collect_financial_data',
                    'symbols' => $symbols
                ];
            } elseif ($dataType === 'sentiment') {
                $params = [
                    'action' => 'analyze_sentiment',
                    'symbols' => $symbols
                ];
            } else {
                throw new Exception("Tipo de datos no válido: {$dataType}");
            }
            
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error en la recopilación de datos: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Obtiene estados financieros (income, balance, cash_flow) desde yfinance
     */
    public function getFinancialStatements(string $symbol): array
    {
        try {
            return $this->executeIntegration([
                'action' => 'get_financial_statements',
                'symbol' => $symbol,
            ]);
        } catch (Exception $e) {
            Log::error('Error fetching financial statements: ' . $e->getMessage());
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }

    /**
     * Obtiene datos históricos OHLCV para un símbolo
     */
    public function getHistoricalData(string $symbol, string $interval = 'daily', ?string $startDate = null, ?string $endDate = null): array
    {
        try {
            $params = [
                'action'     => 'get_historical_data',
                'symbol'     => $symbol,
                'interval'   => $interval,
                'start_date' => $startDate,
                'end_date'   => $endDate,
            ];
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error fetching historical data: ' . $e->getMessage());
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }

    /**
     * Obtiene vista general del mercado (TASI & NOMU)
     */
    public function getMarketOverview(): array
    {
        try {
            return $this->executeIntegration(['action' => 'get_market_overview']);
        } catch (Exception $e) {
            Log::error('Error fetching market overview: ' . $e->getMessage());
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }

    /**
     * Obtiene top movers (gainers, losers, most_active)
     */
    public function getTopMovers(string $type = 'all', int $limit = 5): array
    {
        try {
            return $this->executeIntegration([
                'action' => 'get_top_movers',
                'type'   => $type,
                'limit'  => $limit,
            ]);
        } catch (Exception $e) {
            Log::error('Error fetching top movers: ' . $e->getMessage());
            return ['success' => false, 'error' => $e->getMessage()];
        }
    }

    /**
     * Procesa datos financieros para su análisis
     *
     * @param array $data Datos a procesar
     * @param string $processingType Tipo de procesamiento a aplicar
     * @return array Resultados del procesamiento
     */
    public function processFinancialData(array $data, string $processingType): array
    {
        try {
            $params = [
                'action' => 'process_financial_data',
                'data' => $data,
                'processing_type' => $processingType
            ];
            
            return $this->executeIntegration($params);
        } catch (Exception $e) {
            Log::error('Error en el procesamiento de datos: ' . $e->getMessage());
            return [
                'success' => false,
                'error' => $e->getMessage()
            ];
        }
    }
}