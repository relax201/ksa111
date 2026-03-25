<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class StockPrice extends Model
{
    use HasFactory;

    /**
     * الخصائص التي يمكن تعيينها بشكل جماعي.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'stock_id',
        'date',
        'open',
        'high',
        'low',
        'close',
        'adj_close',
        'volume',
        'change',
        'change_percent',
    ];

    /**
     * الخصائص التي يجب تحويلها.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'date' => 'date',
        'open' => 'decimal:2',
        'high' => 'decimal:2',
        'low' => 'decimal:2',
        'close' => 'decimal:2',
        'adj_close' => 'decimal:2',
        'volume' => 'integer',
        'change' => 'decimal:2',
        'change_percent' => 'decimal:2',
    ];

    /**
     * الحصول على السهم المرتبط بهذا السعر.
     */
    public function stock()
    {
        return $this->belongsTo(Stock::class);
    }

    /**
     * تصفية الأسعار حسب الفترة الزمنية.
     */
    public function scopeInDateRange($query, $startDate, $endDate)
    {
        if ($startDate && $endDate) {
            return $query->whereBetween('date', [$startDate, $endDate]);
        }
        
        if ($startDate) {
            return $query->where('date', '>=', $startDate);
        }
        
        if ($endDate) {
            return $query->where('date', '<=', $endDate);
        }
        
        return $query;
    }

    /**
     * الحصول على أسعار اليوم.
     */
    public function scopeToday($query)
    {
        return $query->whereDate('date', now()->toDateString());
    }

    /**
     * الحصول على أسعار الأسبوع الحالي.
     */
    public function scopeThisWeek($query)
    {
        return $query->whereBetween('date', [
            now()->startOfWeek()->toDateString(),
            now()->endOfWeek()->toDateString()
        ]);
    }

    /**
     * الحصول على أسعار الشهر الحالي.
     */
    public function scopeThisMonth($query)
    {
        return $query->whereBetween('date', [
            now()->startOfMonth()->toDateString(),
            now()->endOfMonth()->toDateString()
        ]);
    }

    /**
     * الحصول على أسعار السنة الحالية.
     */
    public function scopeThisYear($query)
    {
        return $query->whereBetween('date', [
            now()->startOfYear()->toDateString(),
            now()->endOfYear()->toDateString()
        ]);
    }
}