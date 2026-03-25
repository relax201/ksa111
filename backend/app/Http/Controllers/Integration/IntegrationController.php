<?php

namespace App\Http\Controllers\Integration;

use App\Http\Controllers\Controller;
use App\Services\Integration\SystemIntegrationService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

/**
 * IntegrationController
 * 
 * Este controlador maneja las solicitudes relacionadas con la integración de diferentes
 * componentes del sistema, como el motor de recomendación, análisis y recopilación de datos.
 */
class IntegrationController extends Controller
{
    /**
     * @var SystemIntegrationService
     */
    protected $integrationService;

    /**
     * Constructor
     *
     * @param SystemIntegrationService $integrationService
     */
    public function __construct(SystemIntegrationService $integrationService)
    {
        $this->integrationService = $integrationService;
    }

    /**
     * Obtener recomendaciones de inversión
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getRecommendations(Request $request): JsonResponse
    {
        $request->validate([
            'risk_profile' => 'required|string|in:conservative,moderate,aggressive',
            'investment_horizon' => 'required|string|in:short,medium,long',
            'sectors' => 'nullable|array',
            'exclude_symbols' => 'nullable|array',
            'max_results' => 'nullable|integer|min:1|max:50'
        ]);

        $parameters = $request->only([
            'risk_profile',
            'investment_horizon',
            'sectors',
            'exclude_symbols',
            'max_results'
        ]);

        $result = $this->integrationService->executeRecommendationEngine($parameters);

        return response()->json($result);
    }

    /**
     * Obtener análisis técnico para un símbolo
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getTechnicalAnalysis(Request $request): JsonResponse
    {
        $request->validate([
            'symbol' => 'required|string',
            'indicators' => 'required|array',
            'timeframe' => 'nullable|string|in:daily,weekly,monthly'
        ]);

        $symbol = $request->input('symbol');
        $indicators = $request->input('indicators');
        $timeframe = $request->input('timeframe', 'daily');

        $result = $this->integrationService->executeTechnicalAnalysis($symbol, $indicators, $timeframe);

        return response()->json($result);
    }

    /**
     * Obtener análisis fundamental para un símbolo
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getFundamentalAnalysis(Request $request): JsonResponse
    {
        $request->validate([
            'symbol' => 'required|string',
            'metrics' => 'required|array'
        ]);

        $symbol = $request->input('symbol');
        $metrics = $request->input('metrics');

        $result = $this->integrationService->executeFundamentalAnalysis($symbol, $metrics);

        return response()->json($result);
    }

    /**
     * Recopilar datos financieros
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function collectData(Request $request): JsonResponse
    {
        $request->validate([
            'symbols' => 'required|array',
            'data_type' => 'required|string|in:market,financial,sentiment'
        ]);

        $symbols = $request->input('symbols');
        $dataType = $request->input('data_type');

        $result = $this->integrationService->collectData($symbols, $dataType);

        return response()->json($result);
    }

    /**
     * Procesar datos financieros
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function processData(Request $request): JsonResponse
    {
        $request->validate([
            'data' => 'required|array',
            'processing_type' => 'required|string|in:normalization,feature_extraction,time_series'
        ]);

        $data = $request->input('data');
        $processingType = $request->input('processing_type');

        $result = $this->integrationService->processFinancialData($data, $processingType);

        return response()->json($result);
    }
}