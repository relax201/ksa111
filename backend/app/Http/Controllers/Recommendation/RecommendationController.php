<?php

namespace App\Http\Controllers\Recommendation;

use App\Http\Controllers\Controller;
use App\Services\RecommendationService;
use App\Models\Stock;
use App\Models\Recommendation;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Validator;

class RecommendationController extends Controller
{
    protected $recommendationService;
    
    /**
     * إنشاء مثيل جديد من وحدة التحكم.
     *
     * @param RecommendationService $recommendationService
     * @return void
     */
    public function __construct(RecommendationService $recommendationService)
    {
        $this->recommendationService = $recommendationService;
    }
    
    /**
     * الحصول على قائمة التوصيات.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function index(Request $request): JsonResponse
    {
        $filters = [
            'type' => $request->input('type'),
            'action' => $request->input('action'),
            'time_frame' => $request->input('time_frame'),
            'min_confidence' => $request->input('min_confidence'),
            'sector_id' => $request->input('sector_id'),
            'order_by' => $request->input('order_by', 'confidence'),
            'order_direction' => $request->input('order_direction', 'desc'),
            'limit' => $request->input('limit', 10),
        ];
        
        $recommendations = $this->recommendationService->getRecommendations($filters);
        
        return response()->json([
            'status' => 'success',
            'data' => $recommendations,
        ]);
    }
    
    /**
     * الحصول على توصية لسهم معين.
     *
     * @param string $symbol
     * @return JsonResponse
     */
    public function getStockRecommendation($symbol): JsonResponse
    {
        $recommendation = $this->recommendationService->getStockRecommendation($symbol);
        
        if (!$recommendation) {
            return response()->json([
                'status' => 'error',
                'message' => 'لم يتم العثور على توصية لهذا السهم',
            ], 404);
        }
        
        return response()->json([
            'status' => 'success',
            'data' => $recommendation,
        ]);
    }
    
    /**
     * الحصول على توصيات المحفظة.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function getPortfolioRecommendations(Request $request): JsonResponse
    {
        $user = Auth::user();
        
        // الحصول على أسهم المحفظة
        $portfolioStocks = $user->portfolios()
            ->with('stocks')
            ->get()
            ->pluck('stocks')
            ->flatten()
            ->pluck('id')
            ->unique()
            ->toArray();
        
        if (empty($portfolioStocks)) {
            return response()->json([
                'status' => 'error',
                'message' => 'لا توجد أسهم في المحفظة',
            ], 404);
        }
        
        $recommendations = $this->recommendationService->getPortfolioRecommendations($portfolioStocks);
        
        return response()->json([
            'status' => 'success',
            'data' => $recommendations,
        ]);
    }
    
    /**
     * تحديث إعدادات التوصيات.
     *
     * @param Request $request
     * @return JsonResponse
     */
    public function updateSettings(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'min_confidence' => 'nullable|integer|min:0|max:100',
            'time_frame' => 'nullable|in:short,medium,long',
            'recommendation_types' => 'nullable|array',
            'recommendation_types.*' => 'in:technical,fundamental,mixed',
            'notification_enabled' => 'nullable|boolean',
        ]);
        
        if ($validator->fails()) {
            return response()->json([
                'status' => 'error',
                'message' => 'بيانات غير صالحة',
                'errors' => $validator->errors(),
            ], 422);
        }
        
        $user = Auth::user();
        
        // تحديث إعدادات التوصيات للمستخدم
        $user->recommendation_settings = [
            'min_confidence' => $request->input('min_confidence', 50),
            'time_frame' => $request->input('time_frame', 'medium'),
            'recommendation_types' => $request->input('recommendation_types', ['technical', 'fundamental', 'mixed']),
            'notification_enabled' => $request->input('notification_enabled', true),
        ];
        
        $user->save();
        
        return response()->json([
            'status' => 'success',
            'message' => 'تم تحديث إعدادات التوصيات بنجاح',
            'data' => $user->recommendation_settings,
        ]);
    }
}