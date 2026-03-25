<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Portfolio extends Model
{
    use HasFactory;

    protected $fillable = ['user_id', 'name', 'description', 'currency'];

    public function stocks()
    {
        return $this->hasMany(PortfolioStock::class);
    }

    /**
     * حساب إجمالي قيمة الاستثمار بسعر الشراء.
     */
    public function getTotalCostAttribute(): float
    {
        return $this->stocks->sum(fn($s) => $s->quantity * $s->purchase_price);
    }
}
