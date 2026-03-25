<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class PortfolioStock extends Model
{
    use HasFactory;

    protected $fillable = [
        'portfolio_id', 'symbol', 'quantity',
        'purchase_price', 'purchase_date', 'notes',
    ];

    protected $casts = [
        'quantity'       => 'float',
        'purchase_price' => 'float',
        'purchase_date'  => 'date',
    ];

    public function portfolio()
    {
        return $this->belongsTo(Portfolio::class);
    }

    /**
     * إجمالي تكلفة الموقف.
     */
    public function getTotalCostAttribute(): float
    {
        return $this->quantity * $this->purchase_price;
    }
}
