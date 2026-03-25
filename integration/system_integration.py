#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TASI3 System Integration Module

This module provides a unified interface for integrating different components of the TASI3 system,
including the recommendation engine, technical and fundamental analysis, and data collection.

It serves as a central hub for communication between different parts of the system.
"""

import os
import sys
import json
import logging
import importlib
import time
from datetime import datetime
from typing import Dict, List, Any, Union, Optional
import traceback

# ---- Simple in-process cache with TTL ----
_CACHE: Dict[str, Dict] = {}
_CACHE_TTL = int(os.environ.get("TASI3_CACHE_TTL", "300"))  # seconds, default 5 min


def _cache_get(key: str) -> Optional[Any]:
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["value"]
    return None


def _cache_set(key: str, value: Any) -> None:
    _CACHE[key] = {"value": value, "ts": time.time()}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("system_integration")

# Add parent directory to path to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Define component paths
COMPONENTS = {
    "recommendation": {
        "module": "recommendation.engine",
        "class": "RecommendationEngine"
    },
    "technical_analysis": {
        "module": "analysis.technical.analyzer",
        "class": "TechnicalAnalyzer"
    },
    "fundamental_analysis": {
        "module": "analysis.fundamental.analyzer",
        "class": "FundamentalAnalyzer"
    },
    "market_data": {
        "module": "data.collectors.market_data_collector",
        "class": "MarketDataCollector"
    },
    "financial_data": {
        "module": "data.collectors.financial_data_collector",
        "class": "FinancialDataCollector"
    },
    "sentiment_analysis": {
        "module": "data.collectors.sentiment_analyzer",
        "class": "SentimentAnalyzer"
    },
    "data_processor": {
        "module": "data.processors.financial_data_processor",
        "class": "FinancialDataProcessor"
    }
}

class SystemIntegration:
    """
    Main integration class that provides methods to interact with different components
    of the TASI3 system.
    """
    
    def __init__(self):
        """Initialize the integration system."""
        self.components = {}
        logger.info("System Integration initialized")
    
    def _load_component(self, component_name: str) -> Any:
        """
        Dynamically load a component by name.
        
        Args:
            component_name: Name of the component to load
            
        Returns:
            Instance of the component class
        """
        if component_name not in COMPONENTS:
            raise ValueError(f"Unknown component: {component_name}")
            
        if component_name in self.components:
            return self.components[component_name]
            
        try:
            component_info = COMPONENTS[component_name]
            module_name = component_info["module"]
            class_name = component_info["class"]
            
            module = importlib.import_module(module_name)
            component_class = getattr(module, class_name)
            
            if component_name == "market_data":
                try:
                    from integration.config import SAHMAK_API_KEY
                    component_instance = component_class(api_key=SAHMAK_API_KEY)
                except ImportError:
                    logger.warning("Could not import SAHMAK_API_KEY from integration.config")
                    component_instance = component_class()
            else:
                component_instance = component_class()
            
            self.components[component_name] = component_instance
            logger.info(f"Component loaded: {component_name}")
            
            return component_instance
        except Exception as e:
            logger.error(f"Error loading component {component_name}: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def get_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get investment recommendations based on provided parameters.

        Args:
            params: Dictionary containing parameters for recommendation generation
                - risk_profile: Risk profile (conservative, moderate, aggressive)
                - investment_horizon: Investment horizon (short, medium, long)
                - sectors: Optional list of sectors to include
                - exclude_symbols: Optional list of symbols to exclude
                - max_results: Optional maximum number of recommendations

        Returns:
            Dictionary containing recommendation results
        """
        try:
            engine = self._load_component("recommendation")

            # Extract parameters
            risk_profile = params.get("risk_profile", "moderate")
            investment_horizon = params.get("investment_horizon", "medium")
            sectors = params.get("sectors", [])
            exclude_symbols = params.get("exclude_symbols", [])
            max_results = params.get("max_results", 10)

            # Check cache (recommendations are slower, cache for full TTL)
            cache_key = f"recommendations:{risk_profile}:{investment_horizon}:{max_results}"
            cached = _cache_get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return cached

            # Get recommendations from engine
            raw_recommendations = engine.get_recommendations(
                risk_profile=risk_profile,
                investment_horizon=investment_horizon,
                sectors=sectors,
                exclude_symbols=exclude_symbols,
                max_results=max_results
            )

            # Arabic recommendation labels mapping
            rec_map = {
                'strong_buy': 'شراء قوي',
                'buy': 'شراء',
                'hold': 'احتفاظ',
                'sell': 'بيع',
                'strong_sell': 'بيع قوي'
            }

            # Transform each recommendation to the format expected by the frontend
            recommendations = []
            for rec in raw_recommendations:
                ticker = rec.get('ticker', '')
                fundamental = rec.get('components', {}).get('fundamental_analysis', {}) or {}
                # fundamental_analysis is from FundamentalAnalyzer.generate_report()
                # It has: financial_ratios, valuation (intrinsic_value), sector_comparison, etc.
                valuation = fundamental.get('valuation', {}) or {}
                risk_assessment = rec.get('risk_assessment', {}) or {}

                current_price = valuation.get('current_price')
                target_price = valuation.get('estimated_value')

                # Calculate potential upside
                potential = None
                if current_price and target_price and current_price > 0:
                    potential_pct = (target_price - current_price) / current_price * 100
                    potential = f"{potential_pct:+.1f}%"

                # Normalize risk_score to 0-1 (raw score is 0-4)
                raw_risk = risk_assessment.get('risk_score', 0) or 0
                risk_score = min(1.0, raw_risk / 4.0)

                # Use overall score as confidence
                confidence = rec.get('score', 0.5)

                # Get company name and sector from yfinance
                name = ticker
                sector = ''
                try:
                    import yfinance as yf
                    info = yf.Ticker(ticker).info or {}
                    name = info.get('longName') or info.get('shortName') or ticker
                    sector = info.get('sector', '')
                except Exception:
                    pass

                recommendations.append({
                    'symbol': ticker,
                    'name': name,
                    'sector': sector,
                    'recommendation': rec_map.get(rec.get('recommendation', 'hold'), 'احتفاظ'),
                    'current_price': current_price,
                    'target_price': target_price,
                    'potential': potential,
                    'risk_score': round(risk_score, 3),
                    'confidence': round(confidence, 3),
                    'analysis_date': rec.get('analysis_date'),
                    'explanation': rec.get('explanation', ''),
                    'risk_details': risk_assessment.get('specific_risks', [])
                })

            result = {
                "success": True,
                "data": {
                    "recommendations": recommendations,
                    "risk_profile": risk_profile,
                    "investment_horizon": investment_horizon,
                    "analysis_date": datetime.now().strftime('%Y-%m-%d')
                }
            }
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_technical_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get technical analysis for a specific symbol.
        
        Args:
            params: Dictionary containing parameters for technical analysis
                - symbol: Stock symbol
                - indicators: List of technical indicators to calculate
                - timeframe: Optional timeframe (daily, weekly, monthly)
                
        Returns:
            Dictionary containing technical analysis results
        """
        try:
            analyzer = self._load_component("technical_analysis")

            # Extract parameters
            symbol = params.get("symbol")
            indicators = params.get("indicators", [])
            timeframe = params.get("timeframe", "daily")

            if not symbol:
                raise ValueError("Symbol is required")

            if not indicators:
                raise ValueError("At least one indicator is required")

            # Check cache
            cache_key = f"technical:{symbol}:{timeframe}:{','.join(sorted(indicators))}"
            cached = _cache_get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return cached
            
            # Get historical data
            historical_data = analyzer.get_historical_data(symbol, timeframe)
            
            # Calculate indicators
            results = {}
            for indicator in indicators:
                indicator_result = analyzer.calculate_indicator(
                    data=historical_data,
                    indicator=indicator
                )
                if indicator_result is not None:
                    results[indicator] = indicator_result
            
            # Get trend analysis
            trend_analysis = analyzer.analyze_trends(historical_data)
            
            # Extract a simple trend string from trend_analysis
            trend_str = 'neutral'
            if isinstance(trend_analysis, dict):
                assessment = trend_analysis.get('assessment', {}) or {}
                if isinstance(assessment, dict):
                    trend_str = assessment.get('recommendation', 'neutral')
                short_t = trend_analysis.get('trend', {})
                if isinstance(short_t, dict):
                    medium = short_t.get('medium_term', '')
                    if medium in ('bullish', 'bearish'):
                        trend_str = medium

            # Extract support/resistance levels from trend_analysis
            support_levels = []
            resistance_levels = []
            if isinstance(trend_analysis, dict):
                support_levels = trend_analysis.get('support_levels', []) or []
                resistance_levels = trend_analysis.get('resistance_levels', []) or []

            # Get company name
            name = symbol
            try:
                import yfinance as yf
                info = yf.Ticker(symbol).info or {}
                name = info.get('longName') or info.get('shortName') or symbol
            except Exception:
                pass

            result = {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "name": name,
                    "timeframe": timeframe,
                    "indicators": results,
                    "trend_analysis": trend_analysis,
                    "trend": trend_str,
                    "support_levels": support_levels,
                    "resistance_levels": resistance_levels,
                    "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                    "last_updated": analyzer.get_last_update_time(symbol)
                }
            }
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting technical analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_fundamental_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fundamental analysis for a specific symbol.
        
        Args:
            params: Dictionary containing parameters for fundamental analysis
                - symbol: Stock symbol
                - metrics: List of fundamental metrics to calculate
                
        Returns:
            Dictionary containing fundamental analysis results
        """
        try:
            analyzer = self._load_component("fundamental_analysis")

            # Extract parameters
            symbol = params.get("symbol")
            metrics = params.get("metrics", [])

            if not symbol:
                raise ValueError("Symbol is required")

            if not metrics:
                raise ValueError("At least one metric is required")

            # Check cache
            cache_key = f"fundamental:{symbol}:{','.join(sorted(metrics))}"
            cached = _cache_get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                return cached

            # Get financial data
            financial_data = analyzer.get_financial_data(symbol)
            
            # Calculate metrics
            results = {}
            
            # Group metrics by category
            ratio_metrics = [m for m in metrics if m in analyzer.get_available_ratios()]
            valuation_metrics = [m for m in metrics if m in analyzer.get_available_valuations()]
            statement_metrics = [m for m in metrics if m in analyzer.get_available_statement_items()]
            
            # Calculate ratios
            if ratio_metrics:
                results["ratios"] = analyzer.calculate_ratios(financial_data, ratio_metrics)
            
            # Calculate valuations
            if valuation_metrics:
                results["valuations"] = analyzer.calculate_valuations(financial_data, valuation_metrics)
            
            # Get statement items
            if statement_metrics:
                results["statements"] = analyzer.get_statement_items(financial_data, statement_metrics)
            
            # Get company profile
            company_profile = analyzer.get_company_profile(symbol)

            # Determine valuation label from PE ratio
            valuation_label = 'fair'
            pe = results.get('valuations', {}).get('pe_ratio') or results.get('ratios', {}).get('PE')
            if pe is not None:
                if pe < 12:
                    valuation_label = 'undervalued'
                elif pe > 25:
                    valuation_label = 'overvalued'

            result = {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "name": company_profile.get('name', symbol),
                    "metrics": results,
                    "company_profile": company_profile,
                    "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                    "valuation": valuation_label,
                    "sector_comparison": {},
                    "last_updated": analyzer.get_last_update_time(symbol)
                }
            }
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error getting fundamental analysis: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def collect_market_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect market data for specified symbols.
        
        Args:
            params: Dictionary containing parameters for data collection
                - symbols: List of stock symbols
                - data_types: Optional list of market data types to collect
                
        Returns:
            Dictionary containing collected market data
        """
        try:
            collector = self._load_component("market_data")
            
            # Extract parameters
            symbols = params.get("symbols", [])
            data_types = params.get("data_types", ["price", "volume", "market_cap"])
            
            if not symbols:
                raise ValueError("At least one symbol is required")
            
            # Collect market data
            market_data = collector.collect_data(symbols, data_types)
            
            return {
                "success": True,
                "data": market_data,
                "last_updated": collector.get_last_update_time()
            }
        except Exception as e:
            logger.error(f"Error collecting market data: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def collect_financial_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect financial data for specified symbols.
        
        Args:
            params: Dictionary containing parameters for data collection
                - symbols: List of stock symbols
                - statement_types: Optional list of financial statement types
                - periods: Optional list of reporting periods
                
        Returns:
            Dictionary containing collected financial data
        """
        try:
            collector = self._load_component("financial_data")
            
            # Extract parameters
            symbols = params.get("symbols", [])
            statement_types = params.get("statement_types", ["income", "balance", "cash_flow"])
            periods = params.get("periods", ["annual", "quarterly"])
            
            if not symbols:
                raise ValueError("At least one symbol is required")
            
            # Collect financial data
            financial_data = collector.collect_data(symbols, statement_types, periods)
            
            return {
                "success": True,
                "data": financial_data,
                "last_updated": collector.get_last_update_time()
            }
        except Exception as e:
            logger.error(f"Error collecting financial data: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment for specified symbols.
        
        Args:
            params: Dictionary containing parameters for sentiment analysis
                - symbols: List of stock symbols
                - sources: Optional list of sources for sentiment data
                - time_range: Optional time range for sentiment data
                
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            analyzer = self._load_component("sentiment_analysis")
            
            # Extract parameters
            symbols = params.get("symbols", [])
            sources = params.get("sources", ["news", "social_media", "analyst_ratings"])
            time_range = params.get("time_range", "1w")
            
            if not symbols:
                raise ValueError("At least one symbol is required")
            
            # Analyze sentiment
            sentiment_data = analyzer.analyze(symbols, sources, time_range)
            
            return {
                "success": True,
                "data": sentiment_data,
                "analysis_date": analyzer.get_last_update_time()
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_financial_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process financial data.
        
        Args:
            params: Dictionary containing parameters for data processing
                - data: Financial data to process
                - processing_type: Type of processing to apply
                - options: Optional processing options
                
        Returns:
            Dictionary containing processed data
        """
        try:
            processor = self._load_component("data_processor")
            
            # Extract parameters
            data = params.get("data", {})
            processing_type = params.get("processing_type")
            options = params.get("options", {})
            
            if not data:
                raise ValueError("Data is required")
                
            if not processing_type:
                raise ValueError("Processing type is required")
            
            # Process data
            processed_data = processor.process(data, processing_type, options)
            
            return {
                "success": True,
                "data": processed_data
            }
        except Exception as e:
            logger.error(f"Error processing financial data: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }

    def get_financial_statements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch income statement, balance sheet, and cash flow from yfinance.
        Returns data structured for the FinancialData.js component.
        """
        try:
            symbol = params.get("symbol", "")
            if not symbol:
                raise ValueError("Symbol is required")

            cache_key = f"fin_statements_{symbol}"
            cached = _cache_get(cache_key)
            if cached is not None:
                return cached

            ticker_sym = symbol if ("." in symbol or symbol.startswith("^")) else f"{symbol}.SR"

            import yfinance as yf
            ticker = yf.Ticker(ticker_sym)

            def _df_to_periods(df, annual: bool) -> list:
                """Convert a yfinance financials DataFrame to a list of period dicts."""
                if df is None or df.empty:
                    return []
                rows = []
                for col in df.columns:
                    period_label = col.strftime("%Y") if annual else f"Q {col.strftime('%m/%Y')}"
                    row = {"period": period_label}
                    for idx in df.index:
                        try:
                            val = df.loc[idx, col]
                            row[str(idx)] = float(val) if val == val else 0.0  # NaN check
                        except Exception:
                            row[str(idx)] = 0.0
                    rows.append(row)
                return list(reversed(rows))  # oldest first

            def _safe_val(row: dict, *keys) -> float:
                for k in keys:
                    for candidate in row:
                        if k.lower() in candidate.lower():
                            return row[candidate]
                return 0.0

            def _build_income(df, annual: bool) -> list:
                raw = _df_to_periods(df, annual)
                result = []
                for r in raw:
                    revenue = _safe_val(r, "Total Revenue", "Revenue")
                    cogs = _safe_val(r, "Cost Of Revenue", "Cost of Goods")
                    gross = _safe_val(r, "Gross Profit")
                    op_exp = _safe_val(r, "Operating Expense", "Total Operating Expense")
                    op_inc = _safe_val(r, "Operating Income", "EBIT")
                    net = _safe_val(r, "Net Income")
                    result.append({
                        "period": r["period"],
                        "revenue": revenue,
                        "cogs": cogs if cogs else revenue - gross,
                        "grossProfit": gross if gross else revenue - cogs,
                        "operatingExpenses": op_exp,
                        "operatingIncome": op_inc,
                        "netIncome": net,
                    })
                return result

            def _build_balance(df, annual: bool) -> list:
                raw = _df_to_periods(df, annual)
                result = []
                for r in raw:
                    assets = _safe_val(r, "Total Assets")
                    liabilities = _safe_val(r, "Total Liabilities", "Total Liab")
                    equity = _safe_val(r, "Stockholders Equity", "Total Equity", "Common Stock Equity")
                    result.append({
                        "period": r["period"],
                        "assets": assets,
                        "liabilities": liabilities,
                        "equity": equity if equity else assets - liabilities,
                    })
                return result

            def _build_cashflow(df, annual: bool) -> list:
                raw = _df_to_periods(df, annual)
                result = []
                for r in raw:
                    op_cf = _safe_val(r, "Operating Cash Flow", "Total Cash From Operating")
                    inv_cf = _safe_val(r, "Investing Cash Flow", "Total Cash From Investing")
                    fin_cf = _safe_val(r, "Financing Cash Flow", "Total Cash From Financing")
                    net_cf = op_cf + inv_cf + fin_cf
                    result.append({
                        "period": r["period"],
                        "operatingCashFlow": op_cf,
                        "investingCashFlow": inv_cf,
                        "financingCashFlow": fin_cf,
                        "netCashFlow": net_cf,
                    })
                return result

            data = {
                "income": {
                    "annual": _build_income(ticker.financials, True),
                    "quarterly": _build_income(ticker.quarterly_financials, False),
                },
                "balance": {
                    "annual": _build_balance(ticker.balance_sheet, True),
                    "quarterly": _build_balance(ticker.quarterly_balance_sheet, False),
                },
                "cash_flow": {
                    "annual": _build_cashflow(ticker.cashflow, True),
                    "quarterly": _build_cashflow(ticker.quarterly_cashflow, False),
                },
            }

            result = {"success": True, "data": data}
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error fetching financial statements: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_historical_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch OHLCV historical data for a symbol using yfinance.
        """
        try:
            symbol = params.get("symbol", "")
            if not symbol:
                raise ValueError("Symbol is required")

            interval = params.get("interval", "daily")
            start_date = params.get("start_date")
            end_date = params.get("end_date")

            cache_key = f"hist_{symbol}_{interval}_{start_date}_{end_date}"
            cached = _cache_get(cache_key)
            if cached is not None:
                return cached

            yf_interval_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
            yf_interval = yf_interval_map.get(interval, "1d")

            ticker_sym = symbol if ("." in symbol or symbol.startswith("^")) else f"{symbol}.SR"

            import yfinance as yf
            ticker = yf.Ticker(ticker_sym)

            if start_date and end_date:
                hist = ticker.history(start=start_date, end=end_date, interval=yf_interval)
            elif start_date:
                hist = ticker.history(start=start_date, interval=yf_interval)
            else:
                period_map = {"1d": "5d", "1wk": "6mo", "1mo": "2y"}
                hist = ticker.history(period=period_map.get(yf_interval, "1mo"), interval=yf_interval)

            data = []
            for date, row in hist.iterrows():
                open_p = float(row["Open"])
                close_p = float(row["Close"])
                change = round(close_p - open_p, 2)
                change_pct = round((change / open_p * 100), 2) if open_p != 0 else 0.0
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(open_p, 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(close_p, 2),
                    "adj_close": round(close_p, 2),
                    "volume": int(row["Volume"]),
                    "change": change,
                    "change_percent": change_pct,
                })

            result = {"success": True, "data": data}
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_market_overview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch TASI & NOMU index data plus market statistics using yfinance.
        """
        try:
            cached = _cache_get("market_overview_yf")
            if cached is not None:
                return cached

            import yfinance as yf
            from datetime import datetime as _dt

            def _fetch_index(ticker_sym: str, name: str, name_en: str) -> Dict:
                try:
                    info = yf.Ticker(ticker_sym).info or {}
                    price = info.get("regularMarketPrice") or info.get("previousClose") or 0.0
                    change = info.get("regularMarketChange") or 0.0
                    change_pct = info.get("regularMarketChangePercent") or 0.0
                    return {
                        "name": name, "name_en": name_en,
                        "value": round(float(price), 2),
                        "change": round(float(change), 2),
                        "change_percent": round(float(change_pct), 4),
                        "status": "up" if change >= 0 else "down",
                        "last_updated": _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                except Exception:
                    return {"name": name, "name_en": name_en, "value": 0.0, "change": 0.0,
                            "change_percent": 0.0, "status": "unknown",
                            "last_updated": _dt.now().strftime("%Y-%m-%d %H:%M:%S")}

            tasi_info = _fetch_index("^TASI", "مؤشر تاسي", "TASI")
            nomu_info = _fetch_index("^NOMU", "مؤشر نمو", "NOMU")

            result = {
                "success": True,
                "data": {
                    "indices": [tasi_info, nomu_info],
                    "index": tasi_info,
                    "last_updated": _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
            _cache_set("market_overview_yf", result)
            return result
        except Exception as e:
            logger.error(f"Error fetching market overview: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def get_top_movers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch top gainers, losers, and most active Saudi stocks using yfinance.
        """
        try:
            limit = int(params.get("limit", 5))
            mover_type = params.get("type", "all")  # gainers | losers | most_active | all

            cache_key = f"top_movers_{mover_type}_{limit}"
            cached = _cache_get(cache_key)
            if cached is not None:
                return cached

            import yfinance as yf
            from datetime import datetime as _dt

            # Top 30 Saudi stocks by market cap
            SAUDI_TICKERS = [
                "2222.SR", "1180.SR", "2010.SR", "1120.SR", "2380.SR",
                "1211.SR", "2350.SR", "4030.SR", "7010.SR", "2230.SR",
                "1010.SR", "1050.SR", "2330.SR", "4200.SR", "6010.SR",
                "4110.SR", "2050.SR", "3010.SR", "2290.SR", "1030.SR",
                "4050.SR", "1020.SR", "4280.SR", "2070.SR", "3020.SR",
                "4260.SR", "2240.SR", "1140.SR", "4160.SR", "2360.SR",
            ]

            stocks = []
            for ticker_sym in SAUDI_TICKERS:
                try:
                    info = yf.Ticker(ticker_sym).info or {}
                    price = info.get("regularMarketPrice") or info.get("previousClose") or 0.0
                    change = info.get("regularMarketChange") or 0.0
                    change_pct = info.get("regularMarketChangePercent") or 0.0
                    volume = info.get("regularMarketVolume") or 0
                    value = float(price) * float(volume)
                    symbol_clean = ticker_sym.replace(".SR", "")
                    name = info.get("longName") or info.get("shortName") or symbol_clean
                    stocks.append({
                        "symbol": symbol_clean,
                        "name": name,
                        "price": round(float(price), 2),
                        "change": round(float(change), 2),
                        "change_percent": round(float(change_pct), 4),
                        "volume": int(volume),
                        "value": round(value, 2),
                        "status": "up" if change >= 0 else "down",
                    })
                except Exception:
                    continue

            gainers = sorted([s for s in stocks if s["change_percent"] > 0],
                             key=lambda x: x["change_percent"], reverse=True)[:limit]
            losers = sorted([s for s in stocks if s["change_percent"] < 0],
                            key=lambda x: x["change_percent"])[:limit]
            most_active = sorted(stocks, key=lambda x: x["volume"], reverse=True)[:limit]

            result = {
                "success": True,
                "data": {
                    "gainers": gainers,
                    "losers": losers,
                    "most_active": most_active,
                    "last_updated": _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            }
            _cache_set(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error fetching top movers: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}


def parse_input() -> Dict[str, Any]:
    """
    Parse input parameters from command line arguments.
    
    Returns:
        Dictionary containing parsed parameters
    """
    try:
        if len(sys.argv) < 2:
            logger.error("No input parameters provided")
            return {}
        
        # Parse JSON input from command line argument (may be a file path or inline JSON)
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, 'r', encoding='utf-8') as f:
                params_json = f.read()
        else:
            params_json = arg
        params = json.loads(params_json)
        
        logger.info(f"Received parameters: {params}")
        return params
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON input: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error parsing input: {e}")
        return {}

def main():
    """
    Main function to handle integration requests.
    """
    try:
        # Parse input parameters
        params = parse_input()
        if not params:
            result = {
                "success": False,
                "error": "Invalid or missing input parameters"
            }
            print(json.dumps(result))
            return
        
        # Initialize integration system
        integration = SystemIntegration()
        
        # Determine which function to call based on action parameter
        action = params.get("action", "")

        # Map short action names (from bridge.php) to full action names
        action_aliases = {
            "technical": "technical_analysis",
            "fundamental": "fundamental_analysis",
            "market": "collect_market_data",
            "financial": "collect_financial_data",
            "sentiment": "analyze_sentiment",
        }
        action = action_aliases.get(action, action)

        if action == "recommend":
            result = integration.get_recommendations(params)
        elif action == "technical_analysis":
            result = integration.get_technical_analysis(params)
        elif action == "fundamental_analysis":
            result = integration.get_fundamental_analysis(params)
        elif action == "collect_market_data":
            result = integration.collect_market_data(params)
        elif action == "collect_financial_data":
            result = integration.collect_financial_data(params)
        elif action == "analyze_sentiment":
            result = integration.analyze_sentiment(params)
        elif action == "process_financial_data":
            result = integration.process_financial_data(params)
        elif action == "get_financial_statements":
            result = integration.get_financial_statements(params)
        elif action == "get_historical_data":
            result = integration.get_historical_data(params)
        elif action == "get_market_overview":
            result = integration.get_market_overview(params)
        elif action == "get_top_movers":
            result = integration.get_top_movers(params)
        else:
            result = {
                "success": False,
                "error": f"Unknown action: {action}"
            }
        
        # Output result as JSON
        print(json.dumps(result))
    except Exception as e:
        logger.error(f"Unexpected error in integration: {e}")
        logger.error(traceback.format_exc())
        print(json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }))

if __name__ == "__main__":
    main()