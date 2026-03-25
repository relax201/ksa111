<?php

namespace App\Http\Controllers\Analysis;

use App\Http\Controllers\Controller;
use App\Services\Integration\SystemIntegrationService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class AnalysisController extends Controller
{
    public function __construct(
        protected SystemIntegrationService $integrationService
    ) {}

    public function getTechnicalAnalysis(Request $request, string $symbol): JsonResponse
    {
        $timeframe  = $request->get('timeframe', 'daily');
        $indicators = $request->get('indicators', ['SMA', 'RSI', 'MACD', 'BB']);
        if (is_string($indicators)) {
            $indicators = explode(',', $indicators);
        }

        $result = $this->integrationService->executeTechnicalAnalysis($symbol, $indicators, $timeframe);

        if (!($result['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'تعذر إجراء التحليل الفني',
                'error'   => $result['error'] ?? null,
            ], 502);
        }

        return response()->json(['success' => true, 'symbol' => $symbol, 'data' => $result['data'] ?? []]);
    }

    public function getFundamentalAnalysis(Request $request, string $symbol): JsonResponse
    {
        $metrics = $request->get('metrics', ['PE', 'PB', 'ROE', 'ROA', 'profit_margin', 'current_ratio', 'pe_ratio', 'market_cap', 'EPS']);
        if (is_string($metrics)) {
            $metrics = explode(',', $metrics);
        }

        $result = $this->integrationService->executeFundamentalAnalysis($symbol, $metrics);

        if (!($result['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'تعذر إجراء التحليل الأساسي',
                'error'   => $result['error'] ?? null,
            ], 502);
        }

        return response()->json(['success' => true, 'symbol' => $symbol, 'data' => $result['data'] ?? []]);
    }

    public function getIndicators(Request $request, string $symbol): JsonResponse
    {
        $timeframe  = $request->get('timeframe', 'daily');
        $indicators = $request->get('indicators', ['RSI', 'MACD', 'SMA', 'EMA', 'BB', 'Stochastic', 'ADX']);
        if (is_string($indicators)) {
            $indicators = explode(',', $indicators);
        }

        $result = $this->integrationService->executeTechnicalAnalysis($symbol, $indicators, $timeframe);

        if (!($result['success'] ?? false)) {
            return response()->json(['success' => false, 'message' => 'تعذر جلب المؤشرات', 'error' => $result['error'] ?? null], 502);
        }

        return response()->json([
            'success'    => true,
            'symbol'     => $symbol,
            'indicators' => $result['data']['indicators'] ?? [],
            'trend'      => $result['data']['trend'] ?? 'neutral',
            'timeframe'  => $timeframe,
        ]);
    }

    public function getCustomAnalysis(Request $request): JsonResponse
    {
        $request->validate(['symbol' => 'required|string', 'indicators' => 'array', 'metrics' => 'array', 'timeframe' => 'string']);

        $symbol    = $request->input('symbol');
        $timeframe = $request->input('timeframe', 'daily');
        $response  = ['success' => true, 'symbol' => $symbol];

        $indicators = $request->input('indicators', []);
        if (!empty($indicators)) {
            $r = $this->integrationService->executeTechnicalAnalysis($symbol, $indicators, $timeframe);
            $response['technical'] = $r['data'] ?? [];
        }

        $metrics = $request->input('metrics', []);
        if (!empty($metrics)) {
            $r = $this->integrationService->executeFundamentalAnalysis($symbol, $metrics);
            $response['fundamental'] = $r['data'] ?? [];
        }

        return response()->json($response);
    }
}
