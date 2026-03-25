<?php

namespace App\Services;

use App\Services\Integration\SystemIntegrationService;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class RecommendationService
{
    public function __construct(
        protected SystemIntegrationService $integrationService
    ) {}

    /**
     * الحصول على توصيات الأسهم.
     */
    public function getRecommendations(array $filters = []): array
    {
        $cacheKey = 'recommendations_' . md5(json_encode($filters));

        return Cache::remember($cacheKey, config('cache.recommendations_ttl', 1800), function () use ($filters) {
            try {
                $params = [
                    'risk_profile'        => $filters['risk_profile']        ?? 'moderate',
                    'investment_horizon'  => $filters['investment_horizon']  ?? 'medium',
                    'max_results'         => $filters['limit']               ?? 10,
                ];

                if (!empty($filters['sectors'])) {
                    $params['sectors'] = $filters['sectors'];
                }

                $result = $this->integrationService->executeRecommendationEngine($params);

                if (!empty($result['success']) && isset($result['data']['recommendations'])) {
                    return $result['data']['recommendations'];
                }

                return [];
            } catch (\Exception $e) {
                Log::error('Error fetching recommendations: ' . $e->getMessage());
                return [];
            }
        });
    }

    /**
     * الحصول على توصية لسهم معين.
     */
    public function getStockRecommendation(string $symbol): ?array
    {
        $cacheKey = 'stock_recommendation_' . $symbol;

        return Cache::remember($cacheKey, config('cache.recommendations_ttl', 1800), function () use ($symbol) {
            try {
                $result = $this->integrationService->executeRecommendationEngine([
                    'risk_profile'       => 'moderate',
                    'investment_horizon' => 'medium',
                    'max_results'        => 50,
                ]);

                if (empty($result['success']) || empty($result['data']['recommendations'])) {
                    return null;
                }

                $normalizedSymbol = strtoupper(str_replace('.SR', '', $symbol));

                foreach ($result['data']['recommendations'] as $rec) {
                    $recSymbol = strtoupper(str_replace('.SR', '', $rec['symbol'] ?? ''));
                    if ($recSymbol === $normalizedSymbol) {
                        return $rec;
                    }
                }

                return null;
            } catch (\Exception $e) {
                Log::error("Error fetching recommendation for {$symbol}: " . $e->getMessage());
                return null;
            }
        });
    }

    /**
     * الحصول على توصيات للمحفظة.
     */
    public function getPortfolioRecommendations(array $symbols): array
    {
        $cacheKey = 'portfolio_recommendations_' . md5(json_encode($symbols));

        return Cache::remember($cacheKey, config('cache.recommendations_ttl', 1800), function () use ($symbols) {
            try {
                $result = $this->integrationService->executeRecommendationEngine([
                    'risk_profile'       => 'moderate',
                    'investment_horizon' => 'medium',
                    'max_results'        => 50,
                ]);

                if (empty($result['success']) || empty($result['data']['recommendations'])) {
                    return [];
                }

                $normalizedSymbols = array_map(
                    fn($s) => strtoupper(str_replace('.SR', '', $s)),
                    $symbols
                );

                return array_values(array_filter(
                    $result['data']['recommendations'],
                    fn($rec) => in_array(
                        strtoupper(str_replace('.SR', '', $rec['symbol'] ?? '')),
                        $normalizedSymbols
                    )
                ));
            } catch (\Exception $e) {
                Log::error('Error fetching portfolio recommendations: ' . $e->getMessage());
                return [];
            }
        });
    }
}
