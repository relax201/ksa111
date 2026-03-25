<?php

namespace App\Http\Controllers\Market;

use App\Http\Controllers\Controller;
use App\Services\MarketDataService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class MarketController extends Controller
{
    protected $marketDataService;
    
    /**
     * إنشاء مثيل جديد من وحدة التحكم.
     *
     * @param MarketDataService $marketDataService
     * @return void
     */
    public function __construct(MarketDataService $marketDataService)
    {
        $this->marketDataService = $marketDataService;
    }
    
    /**
     * الحصول على نظرة عامة على السوق.
     *
     * @return JsonResponse
     */
    public function getOverview(): JsonResponse
    {
        $overview = $this->marketDataService->getMarketOverview();
        
        return response()->json([
            'status' => 'success',
            'data' => $overview,
        ]);
    }
    
    /**
     * الحصول على قائمة المؤشرات.
     *
     * @return JsonResponse
     */
    public function getIndices(): JsonResponse
    {
        $indices = $this->marketDataService->getIndices();
        
        return response()->json([
            'status' => 'success',
            'data' => $indices,
        ]);
    }
    
    /**
     * الحصول على قائمة القطاعات.
     *
     * @return JsonResponse
     */
    public function getSectors(): JsonResponse
    {
        $sectors = $this->marketDataService->getSectors();
        
        return response()->json([
            'status' => 'success',
            'data' => $sectors,
        ]);
    }
    
    /**
     * الحصول على قائمة الأسهم الأكثر ارتفاعًا.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getTopGainers(Request $request): JsonResponse
    {
        $limit = $request->input('limit', 5);
        $topGainers = $this->marketDataService->getTopGainers($limit);
        
        return response()->json([
            'status' => 'success',
            'data' => $topGainers,
        ]);
    }
    
    /**
     * الحصول على قائمة الأسهم الأكثر انخفاضًا.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getTopLosers(Request $request): JsonResponse
    {
        $limit = $request->input('limit', 5);
        $topLosers = $this->marketDataService->getTopLosers($limit);
        
        return response()->json([
            'status' => 'success',
            'data' => $topLosers,
        ]);
    }
    
    /**
     * الحصول على قائمة الأسهم الأكثر نشاطًا.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getMostActive(Request $request): JsonResponse
    {
        $limit = $request->input('limit', 5);
        $mostActive = $this->marketDataService->getMostActive($limit);
        
        return response()->json([
            'status' => 'success',
            'data' => $mostActive,
        ]);
    }
    
    /**
     * تحديث بيانات السوق.
     *
     * @return JsonResponse
     */
    public function updateMarketData(): JsonResponse
    {
        $result = $this->marketDataService->updateMarketData();
        
        if ($result) {
            return response()->json([
                'status' => 'success',
                'message' => 'تم تحديث بيانات السوق بنجاح',
            ]);
        }
        
        return response()->json([
            'status' => 'error',
            'message' => 'حدث خطأ أثناء تحديث بيانات السوق',
        ], 500);
    }
}