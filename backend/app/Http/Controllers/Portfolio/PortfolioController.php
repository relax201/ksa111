<?php

namespace App\Http\Controllers\Portfolio;

use App\Http\Controllers\Controller;
use App\Models\Portfolio;
use App\Models\PortfolioStock;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Auth;

class PortfolioController extends Controller
{
    /**
     * عرض قائمة المحافظ الاستثمارية للمستخدم الحالي.
     */
    public function index(Request $request): JsonResponse
    {
        $portfolios = Portfolio::with('stocks')
            ->where('user_id', Auth::id())
            ->latest()
            ->get()
            ->map(fn($p) => $this->formatPortfolio($p));

        return response()->json([
            'success' => true,
            'data'    => $portfolios,
            'total'   => $portfolios->count(),
        ]);
    }

    /**
     * إنشاء محفظة جديدة.
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name'        => 'required|string|max:100',
            'description' => 'nullable|string|max:500',
            'currency'    => 'nullable|string|size:3',
        ]);

        $portfolio = Portfolio::create([
            ...$validated,
            'user_id'  => Auth::id(),
            'currency' => $validated['currency'] ?? 'SAR',
        ]);

        return response()->json([
            'success' => true,
            'data'    => $this->formatPortfolio($portfolio->load('stocks')),
            'message' => 'تم إنشاء المحفظة بنجاح',
        ], 201);
    }

    /**
     * عرض تفاصيل محفظة محددة.
     */
    public function show(Request $request, string $id): JsonResponse
    {
        $portfolio = Portfolio::with('stocks')
            ->where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$portfolio) {
            return response()->json([
                'success' => false,
                'message' => 'المحفظة غير موجودة',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data'    => $this->formatPortfolio($portfolio),
        ]);
    }

    /**
     * تحديث بيانات محفظة.
     */
    public function update(Request $request, string $id): JsonResponse
    {
        $portfolio = Portfolio::where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$portfolio) {
            return response()->json([
                'success' => false,
                'message' => 'المحفظة غير موجودة',
            ], 404);
        }

        $validated = $request->validate([
            'name'        => 'sometimes|string|max:100',
            'description' => 'nullable|string|max:500',
        ]);

        $portfolio->update($validated);

        return response()->json([
            'success' => true,
            'data'    => $this->formatPortfolio($portfolio->load('stocks')),
            'message' => 'تم تحديث المحفظة بنجاح',
        ]);
    }

    /**
     * حذف محفظة.
     */
    public function destroy(Request $request, string $id): JsonResponse
    {
        $portfolio = Portfolio::where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$portfolio) {
            return response()->json([
                'success' => false,
                'message' => 'المحفظة غير موجودة',
            ], 404);
        }

        $portfolio->delete();

        return response()->json([
            'success' => true,
            'message' => 'تم حذف المحفظة بنجاح',
        ]);
    }

    /**
     * إضافة سهم إلى المحفظة.
     */
    public function addStock(Request $request, string $id): JsonResponse
    {
        $portfolio = Portfolio::where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$portfolio) {
            return response()->json([
                'success' => false,
                'message' => 'المحفظة غير موجودة',
            ], 404);
        }

        $validated = $request->validate([
            'symbol'        => 'required|string|max:20',
            'quantity'      => 'required|numeric|min:0.0001',
            'price'         => 'required|numeric|min:0',
            'purchase_date' => 'nullable|date',
            'notes'         => 'nullable|string|max:500',
        ]);

        $stock = $portfolio->stocks()->create([
            'symbol'         => strtoupper($validated['symbol']),
            'quantity'       => $validated['quantity'],
            'purchase_price' => $validated['price'],
            'purchase_date'  => $validated['purchase_date'] ?? now()->toDateString(),
            'notes'          => $validated['notes'] ?? null,
        ]);

        return response()->json([
            'success' => true,
            'data'    => $stock,
            'message' => 'تم إضافة السهم إلى المحفظة بنجاح',
        ], 201);
    }

    /**
     * إزالة سهم من المحفظة.
     */
    public function removeStock(Request $request, string $id, string $stockId): JsonResponse
    {
        $portfolio = Portfolio::where('id', $id)
            ->where('user_id', Auth::id())
            ->first();

        if (!$portfolio) {
            return response()->json([
                'success' => false,
                'message' => 'المحفظة غير موجودة',
            ], 404);
        }

        $stock = $portfolio->stocks()->find($stockId);

        if (!$stock) {
            return response()->json([
                'success' => false,
                'message' => 'السهم غير موجود في المحفظة',
            ], 404);
        }

        $stock->delete();

        return response()->json([
            'success' => true,
            'message' => 'تم إزالة السهم من المحفظة بنجاح',
        ]);
    }

    /**
     * تنسيق بيانات المحفظة للاستجابة.
     */
    private function formatPortfolio(Portfolio $portfolio): array
    {
        $stocks = $portfolio->stocks->map(fn($s) => [
            'id'             => $s->id,
            'symbol'         => $s->symbol,
            'quantity'       => $s->quantity,
            'purchase_price' => $s->purchase_price,
            'purchase_date'  => $s->purchase_date?->toDateString(),
            'total_cost'     => round($s->quantity * $s->purchase_price, 2),
            'notes'          => $s->notes,
        ]);

        return [
            'id'          => $portfolio->id,
            'name'        => $portfolio->name,
            'description' => $portfolio->description,
            'currency'    => $portfolio->currency,
            'stocks'      => $stocks,
            'total_cost'  => round($stocks->sum('total_cost'), 2),
            'stocks_count'=> $stocks->count(),
            'created_at'  => $portfolio->created_at->toDateTimeString(),
            'updated_at'  => $portfolio->updated_at->toDateTimeString(),
        ];
    }
}
