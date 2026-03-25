<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Stock extends Model
{
    use HasFactory;

    /**
     * الخصائص التي يمكن تعيينها بشكل جماعي.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'symbol',
        'name',
        'name_en',
        'sector_id',
        'market_id',
        'description',
        'website',
        'email',
        'phone',
        'address',
        'ceo',
        'established_date',
        'listing_date',
        'fiscal_year_end',
        'capital',
        'outstanding_shares',
        'par_value',
        'logo',
        'is_active',
    ];

    /**
     * الخصائص التي يجب تحويلها.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'established_date' => 'date',
        'listing_date' => 'date',
        'capital' => 'decimal:2',
        'outstanding_shares' => 'integer',
        'par_value' => 'decimal:2',
        'is_active' => 'boolean',
    ];

    /**
     * الحصول على القطاع الذي ينتمي إليه السهم.
     */
    public function sector()
    {
        return $this->belongsTo(Sector::class);
    }

    /**
     * الحصول على السوق الذي يتداول فيه السهم.
     */
    public function market()
    {
        return $this->belongsTo(Market::class);
    }

    /**
     * الحصول على بيانات الأسعار التاريخية للسهم.
     */
    public function prices()
    {
        return $this->hasMany(StockPrice::class);
    }

    /**
     * الحصول على البيانات المالية للسهم.
     */
    public function financials()
    {
        return $this->hasMany(StockFinancial::class);
    }

    /**
     * الحصول على توصيات السهم.
     */
    public function recommendations()
    {
        return $this->hasMany(Recommendation::class);
    }

    /**
     * الحصول على أخبار السهم.
     */
    public function news()
    {
        return $this->belongsToMany(News::class, 'stock_news');
    }

    /**
     * الحصول على آخر سعر للسهم.
     */
    public function getLatestPrice()
    {
        return $this->prices()->latest()->first();
    }

    /**
     * البحث عن الأسهم بالاسم أو الرمز.
     */
    public function scopeSearch($query, $term)
    {
        if ($term) {
            return $query->where('name', 'LIKE', "%{$term}%")
                ->orWhere('name_en', 'LIKE', "%{$term}%")
                ->orWhere('symbol', 'LIKE', "%{$term}%");
        }
        
        return $query;
    }

    /**
     * تصفية الأسهم حسب القطاع.
     */
    public function scopeBySector($query, $sectorId)
    {
        if ($sectorId) {
            return $query->where('sector_id', $sectorId);
        }
        
        return $query;
    }

    /**
     * تصفية الأسهم حسب السوق.
     */
    public function scopeByMarket($query, $marketId)
    {
        if ($marketId) {
            return $query->where('market_id', $marketId);
        }
        
        return $query;
    }

    /**
     * تصفية الأسهم النشطة فقط.
     */
    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}