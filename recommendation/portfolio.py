"""
Portfolio Optimization and Management for Saudi Stock Market (Tasi)

This module provides tools for portfolio optimization, risk management,
and performance analysis for Saudi stock portfolios.
"""

import pandas as pd
import numpy as np
import scipy.optimize as sco
from datetime import datetime, timedelta

class PortfolioOptimizer:
    """
    A class for optimizing stock portfolios based on modern portfolio theory
    and other optimization strategies.
    """
    
    def __init__(self, price_data=None, risk_free_rate=0.02):
        """
        Initialize the portfolio optimizer.
        
        Args:
            price_data (DataFrame): Historical price data for stocks
            risk_free_rate (float): Annual risk-free rate
        """
        self.price_data = price_data
        self.returns = None
        self.risk_free_rate = risk_free_rate
        
        if price_data is not None:
            self.calculate_returns()
    
    def set_price_data(self, price_data):
        """
        Set or update the price data.
        
        Args:
            price_data (DataFrame): Historical price data for stocks
        """
        self.price_data = price_data
        self.calculate_returns()
    
    def calculate_returns(self):
        """
        Calculate daily returns from price data.
        """
        if self.price_data is None:
            raise ValueError("Price data not set")
        
        # Calculate daily returns
        self.returns = self.price_data.pct_change().dropna()
    
    def portfolio_performance(self, weights):
        """
        Calculate portfolio performance metrics.
        
        Args:
            weights (array): Portfolio weights
            
        Returns:
            tuple: (expected_return, volatility, sharpe_ratio)
        """
        # Convert annual risk-free rate to daily
        daily_rf = (1 + self.risk_free_rate) ** (1/252) - 1
        
        # Calculate expected returns and covariance
        returns = np.sum(self.returns.mean() * weights) * 252  # Annualized
        volatility = np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights)))
        sharpe_ratio = (returns - self.risk_free_rate) / volatility
        
        return returns, volatility, sharpe_ratio
    
    def negative_sharpe(self, weights):
        """
        Calculate negative Sharpe ratio for optimization.
        
        Args:
            weights (array): Portfolio weights
            
        Returns:
            float: Negative Sharpe ratio
        """
        return -self.portfolio_performance(weights)[2]
    
    def optimize_sharpe(self, constraints=None):
        """
        Optimize portfolio for maximum Sharpe ratio.
        
        Args:
            constraints (list): Additional optimization constraints
            
        Returns:
            dict: Optimized portfolio details
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        num_assets = len(self.returns.columns)
        args = ()
        
        # Initial guess (equal weights)
        init_guess = np.array([1.0 / num_assets] * num_assets)
        
        # Constraints
        bounds = tuple((0, 1) for _ in range(num_assets))
        default_constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if constraints:
            all_constraints = default_constraints + constraints
        else:
            all_constraints = default_constraints
        
        # Optimize
        result = sco.minimize(
            self.negative_sharpe, 
            init_guess,
            args=args,
            method='SLSQP',
            bounds=bounds,
            constraints=all_constraints
        )
        
        # Get optimal weights
        optimal_weights = result['x']
        
        # Calculate performance metrics
        expected_return, volatility, sharpe_ratio = self.portfolio_performance(optimal_weights)
        
        # Create portfolio details
        portfolio = {
            'weights': dict(zip(self.returns.columns, optimal_weights)),
            'performance': {
                'expected_annual_return': expected_return,
                'annual_volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            },
            'optimization_success': result['success']
        }
        
        return portfolio
    
    def optimize_min_volatility(self, target_return=None, constraints=None):
        """
        Optimize portfolio for minimum volatility, optionally with a target return.
        
        Args:
            target_return (float): Target annual return
            constraints (list): Additional optimization constraints
            
        Returns:
            dict: Optimized portfolio details
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        num_assets = len(self.returns.columns)
        
        # Function to minimize (portfolio volatility)
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights)))
        
        # Initial guess (equal weights)
        init_guess = np.array([1.0 / num_assets] * num_assets)
        
        # Constraints
        bounds = tuple((0, 1) for _ in range(num_assets))
        default_constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Add target return constraint if specified
        if target_return is not None:
            def return_constraint(weights):
                return np.sum(self.returns.mean() * weights) * 252 - target_return
            
            default_constraints.append({'type': 'eq', 'fun': return_constraint})
        
        if constraints:
            all_constraints = default_constraints + constraints
        else:
            all_constraints = default_constraints
        
        # Optimize
        result = sco.minimize(
            portfolio_volatility, 
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=all_constraints
        )
        
        # Get optimal weights
        optimal_weights = result['x']
        
        # Calculate performance metrics
        expected_return, volatility, sharpe_ratio = self.portfolio_performance(optimal_weights)
        
        # Create portfolio details
        portfolio = {
            'weights': dict(zip(self.returns.columns, optimal_weights)),
            'performance': {
                'expected_annual_return': expected_return,
                'annual_volatility': volatility,
                'sharpe_ratio': sharpe_ratio
            },
            'optimization_success': result['success']
        }
        
        return portfolio
    
    def efficient_frontier(self, points=20):
        """
        Calculate the efficient frontier.
        
        Args:
            points (int): Number of points on the frontier
            
        Returns:
            DataFrame: Efficient frontier points (return, volatility, sharpe)
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        # Get return range
        min_vol_port = self.optimize_min_volatility()
        max_sharpe_port = self.optimize_sharpe()
        
        min_return = min_vol_port['performance']['expected_annual_return']
        max_return = max_sharpe_port['performance']['expected_annual_return'] * 1.2  # Extend a bit
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, points)
        
        # Calculate efficient portfolios for each target return
        efficient_portfolios = []
        
        for target in target_returns:
            portfolio = self.optimize_min_volatility(target_return=target)
            
            if portfolio['optimization_success']:
                efficient_portfolios.append({
                    'return': portfolio['performance']['expected_annual_return'],
                    'volatility': portfolio['performance']['annual_volatility'],
                    'sharpe': portfolio['performance']['sharpe_ratio']
                })
        
        return pd.DataFrame(efficient_portfolios)
    
    def monte_carlo_simulation(self, num_portfolios=10000):
        """
        Perform Monte Carlo simulation to generate random portfolios.
        
        Args:
            num_portfolios (int): Number of random portfolios to generate
            
        Returns:
            DataFrame: Random portfolios (return, volatility, sharpe, weights)
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        num_assets = len(self.returns.columns)
        results = []
        
        for _ in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            
            # Calculate performance
            returns, volatility, sharpe = self.portfolio_performance(weights)
            
            # Store results
            results.append({
                'return': returns,
                'volatility': volatility,
                'sharpe': sharpe,
                'weights': dict(zip(self.returns.columns, weights))
            })
        
        return pd.DataFrame(results)


class PortfolioAnalyzer:
    """
    A class for analyzing portfolio performance, risk, and characteristics.
    """
    
    def __init__(self, price_data=None, benchmark_data=None, risk_free_rate=0.02):
        """
        Initialize the portfolio analyzer.
        
        Args:
            price_data (DataFrame): Historical price data for portfolio stocks
            benchmark_data (Series): Historical price data for benchmark
            risk_free_rate (float): Annual risk-free rate
        """
        self.price_data = price_data
        self.benchmark_data = benchmark_data
        self.risk_free_rate = risk_free_rate
        self.returns = None
        self.benchmark_returns = None
        
        if price_data is not None:
            self.calculate_returns()
    
    def set_data(self, price_data, benchmark_data=None):
        """
        Set or update the price and benchmark data.
        
        Args:
            price_data (DataFrame): Historical price data for portfolio stocks
            benchmark_data (Series): Historical price data for benchmark
        """
        self.price_data = price_data
        self.benchmark_data = benchmark_data
        self.calculate_returns()
    
    def calculate_returns(self):
        """
        Calculate returns from price data.
        """
        if self.price_data is None:
            raise ValueError("Price data not set")
        
        # Calculate daily returns
        self.returns = self.price_data.pct_change().dropna()
        
        if self.benchmark_data is not None:
            self.benchmark_returns = self.benchmark_data.pct_change().dropna()
    
    def calculate_portfolio_return(self, weights, period='daily'):
        """
        Calculate portfolio returns for a given weight allocation.
        
        Args:
            weights (dict): Portfolio weights by ticker
            period (str): Return period ('daily', 'monthly', 'annual')
            
        Returns:
            Series: Portfolio returns
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        # Convert weights to array in the same order as returns columns
        weight_array = np.array([weights.get(ticker, 0) for ticker in self.returns.columns])
        
        # Normalize weights to sum to 1
        weight_array = weight_array / np.sum(weight_array)
        
        # Calculate portfolio returns
        portfolio_returns = (self.returns * weight_array).sum(axis=1)
        
        # Resample if needed
        if period == 'monthly':
            portfolio_returns = portfolio_returns.resample('M').apply(
                lambda x: (1 + x).prod() - 1
            )
        elif period == 'annual':
            portfolio_returns = portfolio_returns.resample('Y').apply(
                lambda x: (1 + x).prod() - 1
            )
        
        return portfolio_returns
    
    def performance_metrics(self, weights, period='daily'):
        """
        Calculate comprehensive performance metrics for a portfolio.
        
        Args:
            weights (dict): Portfolio weights by ticker
            period (str): Analysis period ('daily', 'monthly', 'annual')
            
        Returns:
            dict: Performance metrics
        """
        # Get portfolio returns
        portfolio_returns = self.calculate_portfolio_return(weights, period)
        
        # Convert annual risk-free rate to match period
        if period == 'daily':
            period_rf = (1 + self.risk_free_rate) ** (1/252) - 1
            annualization_factor = 252
        elif period == 'monthly':
            period_rf = (1 + self.risk_free_rate) ** (1/12) - 1
            annualization_factor = 12
        else:  # annual
            period_rf = self.risk_free_rate
            annualization_factor = 1
        
        # Calculate metrics
        total_return = (1 + portfolio_returns).prod() - 1
        annualized_return = (1 + total_return) ** (annualization_factor / len(portfolio_returns)) - 1
        volatility = portfolio_returns.std() * np.sqrt(annualization_factor)
        sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
        
        # Calculate drawdowns
        wealth_index = (1 + portfolio_returns).cumprod()
        previous_peaks = wealth_index.cummax()
        drawdowns = (wealth_index - previous_peaks) / previous_peaks
        max_drawdown = drawdowns.min()
        
        # Calculate benchmark metrics if available
        benchmark_metrics = None
        if self.benchmark_returns is not None:
            # Resample benchmark returns to match period
            benchmark_period_returns = self.benchmark_returns
            if period == 'monthly':
                benchmark_period_returns = benchmark_period_returns.resample('M').apply(
                    lambda x: (1 + x).prod() - 1
                )
            elif period == 'annual':
                benchmark_period_returns = benchmark_period_returns.resample('Y').apply(
                    lambda x: (1 + x).prod() - 1
                )
            
            # Align benchmark returns with portfolio returns
            aligned_returns = pd.concat([portfolio_returns, benchmark_period_returns], axis=1).dropna()
            if not aligned_returns.empty:
                portfolio_aligned = aligned_returns.iloc[:, 0]
                benchmark_aligned = aligned_returns.iloc[:, 1]
                
                # Calculate beta
                covariance = portfolio_aligned.cov(benchmark_aligned)
                benchmark_variance = benchmark_aligned.var()
                beta = covariance / benchmark_variance if benchmark_variance != 0 else np.nan
                
                # Calculate alpha (Jensen's Alpha)
                portfolio_avg_return = portfolio_aligned.mean() * annualization_factor
                benchmark_avg_return = benchmark_aligned.mean() * annualization_factor
                alpha = portfolio_avg_return - (period_rf + beta * (benchmark_avg_return - period_rf))
                
                # Calculate tracking error
                tracking_error = (portfolio_aligned - benchmark_aligned).std() * np.sqrt(annualization_factor)
                
                # Calculate information ratio
                information_ratio = (portfolio_avg_return - benchmark_avg_return) / tracking_error if tracking_error != 0 else np.nan
                
                benchmark_metrics = {
                    'beta': beta,
                    'alpha': alpha,
                    'tracking_error': tracking_error,
                    'information_ratio': information_ratio,
                    'benchmark_return': (1 + benchmark_aligned).prod() - 1,
                    'benchmark_annualized_return': (1 + benchmark_aligned).prod() ** (annualization_factor / len(benchmark_aligned)) - 1,
                    'benchmark_volatility': benchmark_aligned.std() * np.sqrt(annualization_factor)
                }
        
        # Compile metrics
        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'benchmark_comparison': benchmark_metrics
        }
        
        return metrics
    
    def risk_analysis(self, weights, period='daily'):
        """
        Perform detailed risk analysis for a portfolio.
        
        Args:
            weights (dict): Portfolio weights by ticker
            period (str): Analysis period ('daily', 'monthly', 'annual')
            
        Returns:
            dict: Risk metrics
        """
        # Get portfolio returns
        portfolio_returns = self.calculate_portfolio_return(weights, period)
        
        # Calculate Value at Risk (VaR)
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        
        # Calculate Conditional VaR (CVaR) / Expected Shortfall
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()
        
        # Calculate downside deviation (semi-deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = downside_returns.std() if len(downside_returns) > 0 else 0
        
        # Calculate Sortino ratio
        if period == 'daily':
            annualization_factor = 252
        elif period == 'monthly':
            annualization_factor = 12
        else:  # annual
            annualization_factor = 1
            
        avg_return = portfolio_returns.mean() * annualization_factor
        sortino_ratio = (avg_return - self.risk_free_rate) / (downside_deviation * np.sqrt(annualization_factor)) if downside_deviation != 0 else np.nan
        
        # Calculate maximum drawdown duration
        wealth_index = (1 + portfolio_returns).cumprod()
        previous_peaks = wealth_index.cummax()
        drawdowns = (wealth_index - previous_peaks) / previous_peaks
        
        # Find drawdown periods
        is_drawdown = drawdowns < 0
        drawdown_periods = []
        
        if is_drawdown.any():
            # Convert to numpy for faster processing
            is_drawdown_np = is_drawdown.values
            dates_np = is_drawdown.index.values
            
            # Find start and end of drawdown periods
            drawdown_start = np.where(np.diff(np.hstack(([False], is_drawdown_np))) == 1)[0]
            drawdown_end = np.where(np.diff(np.hstack((is_drawdown_np, [False]))) == -1)[0]
            
            # Calculate drawdown durations and magnitudes
            for start_idx, end_idx in zip(drawdown_start, drawdown_end):
                start_date = pd.Timestamp(dates_np[start_idx])
                end_date = pd.Timestamp(dates_np[end_idx])
                duration = (end_date - start_date).days
                magnitude = drawdowns.iloc[start_idx:end_idx+1].min()
                
                drawdown_periods.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': duration,
                    'magnitude': magnitude
                })
        
        # Find maximum drawdown duration
        max_drawdown_duration = max([p['duration_days'] for p in drawdown_periods]) if drawdown_periods else 0
        
        # Compile risk metrics
        risk_metrics = {
            'value_at_risk_95': var_95,
            'value_at_risk_99': var_99,
            'conditional_var_95': cvar_95,
            'conditional_var_99': cvar_99,
            'downside_deviation': downside_deviation,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': drawdowns.min(),
            'max_drawdown_duration_days': max_drawdown_duration,
            'drawdown_periods': drawdown_periods
        }
        
        return risk_metrics
    
    def correlation_analysis(self):
        """
        Analyze correlations between assets in the portfolio.
        
        Returns:
            DataFrame: Correlation matrix
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        return self.returns.corr()
    
    def rolling_performance(self, weights, window=252, metric='return'):
        """
        Calculate rolling performance metrics.
        
        Args:
            weights (dict): Portfolio weights by ticker
            window (int): Rolling window size in days
            metric (str): Metric to calculate ('return', 'volatility', 'sharpe')
            
        Returns:
            Series: Rolling performance metric
        """
        # Get portfolio returns
        portfolio_returns = self.calculate_portfolio_return(weights, 'daily')
        
        if metric == 'return':
            # Calculate rolling annualized return
            rolling_return = portfolio_returns.rolling(window).apply(
                lambda x: (1 + x).prod() ** (252 / len(x)) - 1
            )
            return rolling_return
            
        elif metric == 'volatility':
            # Calculate rolling annualized volatility
            rolling_volatility = portfolio_returns.rolling(window).std() * np.sqrt(252)
            return rolling_volatility
            
        elif metric == 'sharpe':
            # Calculate rolling Sharpe ratio
            daily_rf = (1 + self.risk_free_rate) ** (1/252) - 1
            
            def rolling_sharpe(x):
                if len(x) < 2:
                    return np.nan
                ret = (1 + x).prod() ** (252 / len(x)) - 1
                vol = x.std() * np.sqrt(252)
                return (ret - self.risk_free_rate) / vol if vol != 0 else np.nan
            
            rolling_sharpe = portfolio_returns.rolling(window).apply(rolling_sharpe)
            return rolling_sharpe
            
        else:
            raise ValueError(f"Unsupported metric: {metric}")
    
    def performance_attribution(self, weights, period='monthly'):
        """
        Perform performance attribution analysis.
        
        Args:
            weights (dict): Portfolio weights by ticker
            period (str): Analysis period ('daily', 'monthly', 'annual')
            
        Returns:
            dict: Attribution analysis results
        """
        if self.returns is None:
            raise ValueError("Returns data not calculated")
        
        # Resample returns if needed
        if period == 'monthly':
            period_returns = self.returns.resample('M').apply(
                lambda x: (1 + x).prod() - 1
            )
        elif period == 'annual':
            period_returns = self.returns.resample('Y').apply(
                lambda x: (1 + x).prod() - 1
            )
        else:  # daily
            period_returns = self.returns
        
        # Calculate portfolio return
        portfolio_return = self.calculate_portfolio_return(weights, period)
        
        # Calculate contribution of each asset
        weight_array = np.array([weights.get(ticker, 0) for ticker in period_returns.columns])
        weight_array = weight_array / np.sum(weight_array)
        
        # Calculate average return for each asset
        asset_returns = period_returns.mean()
        
        # Calculate contribution to return
        contribution = asset_returns * weight_array
        
        # Calculate attribution
        attribution = {
            'asset_returns': dict(zip(period_returns.columns, asset_returns)),
            'contribution': dict(zip(period_returns.columns, contribution)),
            'weights': dict(zip(period_returns.columns, weight_array)),
            'portfolio_return': portfolio_return.mean()
        }
        
        return attribution