<?php

namespace App\Http\Controllers\News;

use App\Http\Controllers\Controller;
use App\Models\News;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Cache;

class NewsController extends Controller
{
    /**
     * قائمة الأخبار مع التصفية والترقيم.
     */
    public function index(Request $request): JsonResponse
    {
        $category = $request->get('category');
        $symbol   = $request->get('symbol');
        $perPage  = (int) $request->get('per_page', 20);

        $query = News::published()->latest('published_at');

        if ($category) {
            $query->byCategory($category);
        }

        if ($symbol) {
            $query->whereHas('stocks', fn($q) => $q->where('symbol', strtoupper($symbol)));
        }

        $paginated = $query->paginate($perPage);

        return response()->json([
            'success' => true,
            'data'    => $paginated->items(),
            'total'   => $paginated->total(),
            'pagination' => [
                'current_page' => $paginated->currentPage(),
                'last_page'    => $paginated->lastPage(),
                'per_page'     => $paginated->perPage(),
            ],
        ]);
    }

    /**
     * تفاصيل خبر محدد.
     */
    public function show(Request $request, string $id): JsonResponse
    {
        $news = News::published()->find($id);

        if (!$news) {
            return response()->json([
                'success' => false,
                'message' => 'الخبر غير موجود',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data'    => $news,
        ]);
    }

    /**
     * فئات الأخبار المتاحة.
     */
    public function getCategories(Request $request): JsonResponse
    {
        return response()->json([
            'success' => true,
            'data'    => [
                ['id' => 'market',        'name' => 'السوق'],
                ['id' => 'companies',     'name' => 'الشركات'],
                ['id' => 'economy',       'name' => 'الاقتصاد'],
                ['id' => 'international', 'name' => 'دولي'],
            ],
        ]);
    }
}
