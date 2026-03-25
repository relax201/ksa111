<?php

namespace App\Http\Controllers\Stock;

use App\Http\Controllers\Controller;
use App\Services\MarketDataService;
use App\Services\Integration\SystemIntegrationService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class StockController extends Controller
{
    public function __construct(
        protected MarketDataService $marketDataService,
        protected SystemIntegrationService $integrationService
    ) {}

    /**
     * قائمة الأسهم الأكثر نشاطاً مع دعم البحث.
     */
    public function index(Request $request): JsonResponse
    {
        $symbolFilter = $request->get('symbol');
        $stocks = $this->marketDataService->getMostActive(50);

        if ($symbolFilter) {
            $stocks = array_values(array_filter(
                $stocks,
                fn($s) => stripos($s['symbol'] ?? '', $symbolFilter) !== false
                       || stripos($s['name'] ?? '', $symbolFilter) !== false
            ));
        }

        return response()->json([
            'success' => true,
            'data'    => array_values($stocks),
            'total'   => count($stocks),
        ]);
    }

    /**
     * تفاصيل سهم محدد عبر Python/yfinance.
     */
    public function show(Request $request, string $symbol): JsonResponse
    {
        $result = $this->integrationService->executeFundamentalAnalysis(
            $symbol,
            ['PE', 'PB', 'ROE', 'ROA', 'profit_margin', 'current_ratio',
             'pe_ratio', 'pb_ratio', 'dividend_yield', 'market_cap', 'revenue', 'net_income', 'EPS']
        );

        if (!($result['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'تعذر جلب بيانات السهم',
                'error'   => $result['error'] ?? null,
            ], 502);
        }

        $data = $result['data'] ?? [];

        return response()->json([
            'success' => true,
            'data'    => [
                'symbol'        => $symbol,
                'name'          => $data['name'] ?? $symbol,
                'sector'        => $data['company_profile']['sector'] ?? '',
                'industry'      => $data['company_profile']['industry'] ?? '',
                'description'   => $data['company_profile']['description'] ?? '',
                'website'       => $data['company_profile']['website'] ?? '',
                'employees'     => $data['company_profile']['employees'] ?? null,
                'metrics'       => $data['metrics'] ?? [],
                'valuation'     => $data['valuation'] ?? 'fair',
                'analysis_date' => $data['analysis_date'] ?? now()->toDateString(),
            ],
        ]);
    }

    /**
     * البيانات التاريخية عبر MarketDataService.
     */
    public function getHistoricalData(Request $request, string $symbol): JsonResponse
    {
        $interval  = $request->get('interval', 'daily');
        $startDate = $request->get('start_date');
        $endDate   = $request->get('end_date');

        $data = $this->marketDataService->getHistoricalData($symbol, $interval, $startDate, $endDate);

        return response()->json([
            'success'  => true,
            'symbol'   => $symbol,
            'interval' => $interval,
            'data'     => $data,
            'total'    => count($data),
        ]);
    }

    /**
     * تحليل المشاعر لسهم محدد عبر Python/SentimentAnalyzer.
     */
    public function getSentiment(Request $request, string $symbol): JsonResponse
    {
        $result = $this->integrationService->collectData([$symbol], 'sentiment');

        if (!($result['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'تعذر جلب بيانات المشاعر',
                'error'   => $result['error'] ?? null,
            ], 502);
        }

        // Remap: Python returns data keyed by "SYMBOL.SR"; expose clean keys
        $rawData  = $result['data'] ?? [];
        $mapped   = [];
        foreach ($rawData as $key => $value) {
            $cleanKey = str_replace('.SR', '', $key);
            $mapped[$cleanKey] = $value;
        }

        return response()->json([
            'success'       => true,
            'symbols'       => [$symbol],
            'sentiment'     => $mapped,
            'analysis_date' => $result['analysis_date'] ?? now()->toDateString(),
        ]);
    }

    /**
     * القوائم المالية (دخل، ميزانية، تدفقات نقدية) عبر yfinance.
     */
    public function getFinancials(Request $request, string $symbol): JsonResponse
    {
        $result = $this->integrationService->getFinancialStatements($symbol);

        if (!($result['success'] ?? false)) {
            return response()->json([
                'success' => false,
                'message' => 'تعذر جلب القوائم المالية',
                'error'   => $result['error'] ?? null,
            ], 502);
        }

        return response()->json([
            'success' => true,
            'symbol'  => $symbol,
            'data'    => $result['data'] ?? [],
        ]);
    }

    /**
     * ملف الشركة الكامل عبر Python/yfinance.
     */
    public function getProfile(Request $request, string $symbol): JsonResponse
    {
        $result = $this->integrationService->executeFundamentalAnalysis(
            $symbol,
            ['PE', 'PB', 'ROE', 'revenue', 'net_income', 'EPS', 'market_cap', 'dividend_yield']
        );

        $profile = ['symbol' => $symbol];
        if ($result['success'] ?? false) {
            $data           = $result['data'] ?? [];
            $profile        = array_merge($profile, $data['company_profile'] ?? []);
            $profile['metrics'] = $data['metrics'] ?? [];
        }

        return response()->json([
            'success' => true,
            'symbol'  => $symbol,
            'profile' => $profile,
        ]);
    }
}
