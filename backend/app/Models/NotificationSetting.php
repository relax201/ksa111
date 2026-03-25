<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class NotificationSetting extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'email_notifications',
        'price_alerts',
        'recommendation_alerts',
        'market_news',
    ];

    protected $casts = [
        'email_notifications'   => 'boolean',
        'price_alerts'          => 'boolean',
        'recommendation_alerts' => 'boolean',
        'market_news'           => 'boolean',
    ];
}
