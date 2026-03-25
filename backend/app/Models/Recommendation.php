<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Recommendation extends Model
{
    use HasFactory;

    /**
     * الخصائص التي يمكن تعيينها بشكل جماعي.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'stock_id',
        'type',
        'action',
        'price',
        'target_price',
        'stop_loss',
        'confidence',
        'time_frame',
        'analysis_date',
        'expiry_date',
        'status',
        'notes',
        'technical_indicators',
        'fundamental_indicators',
    ];

    /**
     * الخصائص التي يجب تحويلها.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'price' => 'decimal:2',
        'target_price' => 'decimal:2',
        'stop_loss' => 'decimal:2',
        'confidence' => 'integer',
        'analysis_date' => 'datetime',
        'expiry_date' => 'datetime',
        'technical_indicators' => 'array',
        'fundamental_indicators' => 'array',
    ];

    /**
     * قيم ثابتة لأنواع التوصيات.
     */
    const TYPE_TECHNICAL = 'technical';
    const TYPE_FUNDAMENTAL = 'fundamental';
    const TYPE_MIXED = 'mixed';

    /**
     * قيم ثابتة لإجراءات التوصيات.
     */
    const ACTION_BUY = 'buy';
    const ACTION_SELL = 'sell';
    const ACTION_HOLD = 'hold';

    /**
     * قيم ثابتة لحالات التوصيات.
     */
    const STATUS_ACTIVE = 'active';
    const STATUS_ACHIEVED = 'achieved';
    const STATUS_EXPIRED = 'expired';
    const STATUS_STOPPED = 'stopped';

    /**
     * الحصول على السهم المرتبط بهذه التوصية.
     */
    public function stock()
    {
        return $this->belongsTo(Stock::class);
    }

    /**
     * تصفية التوصيات النشطة.
     */
    public function scopeActive($query)
    {
        return $query->where('status', self::STATUS_ACTIVE);
    }

    /**
     * تصفية التوصيات حسب النوع.
     */
    public function scopeByType($query, $type)
    {
        if ($type) {
            return $query->where('type', $type);
        }
        
        return $query;
    }

    /**
     * تصفية التوصيات حسب الإجراء.
     */
    public function scopeByAction($query, $action)
    {
        if ($action) {
            return $query->where('action', $action);
        }
        
        return $query;
    }

    /**
     * تصفية التوصيات حسب الفترة الزمنية.
     */
    public function scopeByTimeFrame($query, $timeFrame)
    {
        if ($timeFrame) {
            return $query->where('time_frame', $timeFrame);
        }
        
        return $query;
    }

    /**
     * تصفية التوصيات حسب مستوى الثقة.
     */
    public function scopeByConfidence($query, $minConfidence)
    {
        if ($minConfidence) {
            return $query->where('confidence', '>=', $minConfidence);
        }
        
        return $query;
    }

    /**
     * حساب نسبة الربح المحتمل.
     */
    public function getPotentialReturnAttribute()
    {
        if ($this->price > 0) {
            return (($this->target_price - $this->price) / $this->price) * 100;
        }
        
        return 0;
    }

    /**
     * حساب نسبة المخاطرة.
     */
    public function getRiskRatioAttribute()
    {
        if ($this->price > 0 && $this->stop_loss > 0) {
            $potentialLoss = abs(($this->stop_loss - $this->price) / $this->price) * 100;
            $potentialGain = abs(($this->target_price - $this->price) / $this->price) * 100;
            
            if ($potentialLoss > 0) {
                return $potentialGain / $potentialLoss;
            }
        }
        
        return 0;
    }
}