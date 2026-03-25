<?php

namespace App\Services;

use App\Services\Integration\SystemIntegrationService;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;

class MarketDataService
{
    public function __construct(
        protected SystemIntegrationService $integrationService
    ) {}

    /**
     * الحصول على نظرة عامة على السوق.
     */
    public function getMarketOverview(): array
    {
        return Cache::remember('market_overview', config('cache.market_data_ttl', 300), function () {
            try {
                $response = $this->integrationService->getMarketOverview();
                if (!empty($response['success']) && isset($response['data'])) {
                    return $response['data'];
                }
                Log::warning('Market overview fallback to default data');
                return $this->getDefaultMarketOverview();
            } catch (\Exception $e) {
                Log::error('Error fetching market overview: ' . $e->getMessage());
                return $this->getDefaultMarketOverview();
            }
        });
    }

    /**
     * الحصول على قائمة المؤشرات.
     */
    public function getIndices(): array
    {
        return Cache::remember('market_indices', config('cache.market_data_ttl', 300), function () {
            try {
                $response = $this->integrationService->getMarketOverview();
                if (!empty($response['success']) && isset($response['data']['indices'])) {
                    return $response['data']['indices'];
                }
                return $this->getDefaultIndices();
            } catch (\Exception $e) {
                Log::error('Error fetching market indices: ' . $e->getMessage());
                return $this->getDefaultIndices();
            }
        });
    }

    /**
     * الحصول على قائمة القطاعات.
     */
    public function getSectors(): array
    {
        return Cache::remember('market_sectors', config('cache.market_data_ttl', 300), function () {
            return $this->getDefaultSectors();
        });
    }

    /**
     * الحصول على قائمة الأسهم الأكثر ارتفاعًا.
     */
    public function getTopGainers(int $limit = 5): array
    {
        return Cache::remember('top_gainers_' . $limit, config('cache.market_data_ttl', 300), function () use ($limit) {
            try {
                $response = $this->integrationService->getTopMovers('gainers', $limit);
                if (!empty($response['success']) && isset($response['data']['gainers'])) {
                    return $response['data']['gainers'];
                }
                return $this->getDefaultTopGainers($limit);
            } catch (\Exception $e) {
                Log::error('Error fetching top gainers: ' . $e->getMessage());
                return $this->getDefaultTopGainers($limit);
            }
        });
    }

    /**
     * الحصول على قائمة الأسهم الأكثر انخفاضًا.
     */
    public function getTopLosers(int $limit = 5): array
    {
        return Cache::remember('top_losers_' . $limit, config('cache.market_data_ttl', 300), function () use ($limit) {
            try {
                $response = $this->integrationService->getTopMovers('losers', $limit);
                if (!empty($response['success']) && isset($response['data']['losers'])) {
                    return $response['data']['losers'];
                }
                return $this->getDefaultTopLosers($limit);
            } catch (\Exception $e) {
                Log::error('Error fetching top losers: ' . $e->getMessage());
                return $this->getDefaultTopLosers($limit);
            }
        });
    }

    /**
     * الحصول على قائمة الأسهم الأكثر نشاطًا.
     */
    public function getMostActive(int $limit = 5): array
    {
        return Cache::remember('most_active_' . $limit, config('cache.market_data_ttl', 300), function () use ($limit) {
            try {
                $response = $this->integrationService->getTopMovers('most_active', $limit);
                if (!empty($response['success']) && isset($response['data']['most_active'])) {
                    return $response['data']['most_active'];
                }
                return $this->getDefaultMostActive($limit);
            } catch (\Exception $e) {
                Log::error('Error fetching most active: ' . $e->getMessage());
                return $this->getDefaultMostActive($limit);
            }
        });
    }

    /**
     * الحصول على البيانات التاريخية لسهم معين.
     */
    public function getHistoricalData(string $symbol, string $interval = 'daily', ?string $startDate = null, ?string $endDate = null): array
    {
        $cacheKey = "historical_{$symbol}_{$interval}_{$startDate}_{$endDate}";

        return Cache::remember($cacheKey, config('cache.stock_data_ttl', 600), function () use ($symbol, $interval, $startDate, $endDate) {
            try {
                $response = $this->integrationService->getHistoricalData($symbol, $interval, $startDate, $endDate);
                if (!empty($response['success']) && isset($response['data'])) {
                    return $response['data'];
                }
                Log::warning("Historical data fallback for {$symbol}");
                return $this->getDefaultHistoricalData($symbol, $interval, $startDate, $endDate);
            } catch (\Exception $e) {
                Log::error("Error fetching historical data for {$symbol}: " . $e->getMessage());
                return $this->getDefaultHistoricalData($symbol, $interval, $startDate, $endDate);
            }
        });
    }

    /**
     * تحديث بيانات السوق ومسح الكاش.
     */
    public function updateMarketData(): bool
    {
        try {
            $this->clearMarketDataCache();
            return true;
        } catch (\Exception $e) {
            Log::error('Error updating market data: ' . $e->getMessage());
            return false;
        }
    }

    private function clearMarketDataCache(): void
    {
        foreach (['market_overview', 'market_indices', 'market_sectors',
                  'top_gainers_5', 'top_losers_5', 'most_active_5'] as $key) {
            Cache::forget($key);
        }
    }

    // ── Fallback default data ──────────────────────────────────────────────

    private function getDefaultMarketOverview(): array
    {
        return [
            'index' => [
                'name'           => 'مؤشر تاسي',
                'value'          => 11290.45,
                'change'         => 23.67,
                'change_percent' => 0.21,
                'status'         => 'up',
                'last_updated'   => Carbon::now()->format('Y-m-d H:i:s'),
            ],
            'statistics' => [
                'volume'     => 5234567890,
                'value'      => 9876543210,
                'trades'     => 324567,
                'market_cap' => 9876543210000,
            ],
            'advances_declines' => [
                'advances'  => 87,
                'declines'  => 65,
                'unchanged' => 23,
            ],
            'market_status' => [
                'status'           => 'open',
                'message'          => 'السوق مفتوح',
                'next_event'       => 'إغلاق',
                'next_event_time'  => Carbon::now()->addHours(3)->format('H:i:s'),
            ],
        ];
    }

    private function getDefaultIndices(): array
    {
        return [
            ['id' => 1, 'name' => 'مؤشر تاسي', 'name_en' => 'TASI',
             'value' => 11290.45, 'change' => 23.67, 'change_percent' => 0.21,
             'status' => 'up', 'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
            ['id' => 2, 'name' => 'مؤشر نمو', 'name_en' => 'NOMU',
             'value' => 24567.89, 'change' => -45.67, 'change_percent' => -0.19,
             'status' => 'down', 'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
        ];
    }

    private function getDefaultSectors(): array
    {
        return [
            ['id' => 1, 'name' => 'البنوك',       'name_en' => 'Banks',              'value' => 5678.90, 'change' =>  12.34, 'change_percent' =>  0.22, 'status' => 'up',   'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
            ['id' => 2, 'name' => 'الطاقة',       'name_en' => 'Energy',             'value' => 6789.01, 'change' => -23.45, 'change_percent' => -0.34, 'status' => 'down', 'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
            ['id' => 3, 'name' => 'الاتصالات',    'name_en' => 'Telecommunication',  'value' => 7890.12, 'change' =>  34.56, 'change_percent' =>  0.44, 'status' => 'up',   'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
            ['id' => 4, 'name' => 'المواد الأساسية', 'name_en' => 'Materials',       'value' => 4567.23, 'change' =>   8.90, 'change_percent' =>  0.20, 'status' => 'up',   'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
            ['id' => 5, 'name' => 'الصناعة',      'name_en' => 'Industrials',        'value' => 3456.78, 'change' =>  -5.67, 'change_percent' => -0.16, 'status' => 'down', 'last_updated' => Carbon::now()->format('Y-m-d H:i:s')],
        ];
    }

    private function getDefaultTopGainers(int $limit = 5): array
    {
        return array_slice([
            ['symbol' => '2222', 'name' => 'أرامكو السعودية', 'price' => 34.50, 'change' => 0.90, 'change_percent' => 2.68, 'volume' => 12345678],
            ['symbol' => '1180', 'name' => 'أل راجحي',        'price' => 87.20, 'change' => 2.10, 'change_percent' => 2.47, 'volume' =>  4567890],
            ['symbol' => '2010', 'name' => 'سابك',            'price' => 98.40, 'change' => 2.20, 'change_percent' => 2.29, 'volume' =>  3456789],
            ['symbol' => '1120', 'name' => 'الراجحي',         'price' => 78.60, 'change' => 1.60, 'change_percent' => 2.08, 'volume' =>  2345678],
            ['symbol' => '2380', 'name' => 'بترو رابغ',       'price' => 23.40, 'change' => 0.40, 'change_percent' => 1.74, 'volume' =>  1234567],
        ], 0, $limit);
    }

    private function getDefaultTopLosers(int $limit = 5): array
    {
        return array_slice([
            ['symbol' => '4030', 'name' => 'الاتصالات السعودية', 'price' => 45.20, 'change' => -1.20, 'change_percent' => -2.59, 'volume' =>  5678901],
            ['symbol' => '7010', 'name' => 'سافكو',              'price' => 32.60, 'change' => -0.80, 'change_percent' => -2.40, 'volume' =>  3456789],
            ['symbol' => '2230', 'name' => 'شركة الكيمياء',      'price' => 56.80, 'change' => -1.20, 'change_percent' => -2.07, 'volume' =>  2345678],
            ['symbol' => '1211', 'name' => 'معدنية',             'price' => 18.40, 'change' => -0.36, 'change_percent' => -1.92, 'volume' =>  1234567],
            ['symbol' => '2350', 'name' => 'سيمكو',              'price' => 54.60, 'change' => -1.00, 'change_percent' => -1.80, 'volume' =>   987654],
        ], 0, $limit);
    }

    private function getDefaultMostActive(int $limit = 5): array
    {
        return array_slice([
            ['symbol' => '2222', 'name' => 'أرامكو السعودية',    'price' => 34.50, 'change' =>  0.90, 'change_percent' =>  2.68, 'volume' => 12345678, 'value' => 426426001.00],
            ['symbol' => '1180', 'name' => 'أل راجحي',           'price' => 87.20, 'change' =>  2.10, 'change_percent' =>  2.47, 'volume' =>  4567890, 'value' => 398320008.00],
            ['symbol' => '4030', 'name' => 'الاتصالات السعودية', 'price' => 45.20, 'change' => -1.20, 'change_percent' => -2.59, 'volume' =>  5678901, 'value' => 256686325.20],
            ['symbol' => '2010', 'name' => 'سابك',               'price' => 98.40, 'change' =>  2.20, 'change_percent' =>  2.29, 'volume' =>  3456789, 'value' => 340148427.60],
            ['symbol' => '7010', 'name' => 'سافكو',              'price' => 32.60, 'change' => -0.80, 'change_percent' => -2.40, 'volume' =>  3456789, 'value' => 112691323.40],
        ], 0, $limit);
    }

    private function getDefaultHistoricalData(string $_symbol, string $interval = 'daily', ?string $startDate = null, ?string $endDate = null): array
    {
        $data = [];
        $start  = $startDate ? Carbon::parse($startDate) : Carbon::now()->subDays(30);
        $end    = $endDate   ? Carbon::parse($endDate)   : Carbon::now();
        $current    = clone $start;
        $basePrice  = 50.0;

        while ($current <= $end) {
            if (!in_array($current->dayOfWeek, [Carbon::FRIDAY, Carbon::SATURDAY])) {
                $change    = (mt_rand(-100, 100) / 100) * 2;
                $price     = max(1.0, $basePrice + $change);
                $basePrice = $price;
                $open      = $price - (mt_rand(-50, 50) / 100);
                $high      = max($price, $open) + (mt_rand(10, 50) / 100);
                $low       = min($price, $open) - (mt_rand(10, 50) / 100);

                $data[] = [
                    'date'           => $current->format('Y-m-d'),
                    'open'           => round($open, 2),
                    'high'           => round($high, 2),
                    'low'            => round($low, 2),
                    'close'          => round($price, 2),
                    'adj_close'      => round($price, 2),
                    'volume'         => mt_rand(100000, 1000000),
                    'change'         => round($change, 2),
                    'change_percent' => round(($price - $open) / max($open, 0.01) * 100, 2),
                ];
            }

            match ($interval) {
                'weekly'  => $current->addWeek(),
                'monthly' => $current->addMonth(),
                default   => $current->addDay(),
            };
        }

        return $data;
    }
}
