"""
Valuation Models Module for Saudi Stock Market (Tasi)

This module provides tools for valuing Saudi companies using various
valuation models including DCF, dividend discount, and relative valuation.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class ValuationModel:
    """
    Base class for valuation models.
    """
    
    def __init__(self, financial_data=None, market_data=None):
        """
        Initialize the valuation model.
        
        Args:
            financial_data (dict): Financial statements data
            market_data (dict): Market data including price, shares outstanding, etc.
        """
        self.financial_data = financial_data or {}
        self.market_data = market_data or {}
    
    def set_data(self, financial_data=None, market_data=None):
        """
        Set or update data.
        
        Args:
            financial_data (dict): Financial statements data
            market_data (dict): Market data
        """
        if financial_data:
            self.financial_data = financial_data
        
        if market_data:
            self.market_data = market_data
    
    def get_current_price(self):
        """
        Get current market price.
        
        Returns:
            float: Current price
        """
        return self.market_data.get('price')
    
    def get_shares_outstanding(self):
        """
        Get shares outstanding.
        
        Returns:
            float: Shares outstanding
        """
        return self.market_data.get('shares_outstanding')
    
    def get_market_cap(self):
        """
        Calculate market capitalization.
        
        Returns:
            float: Market capitalization
        """
        price = self.get_current_price()
        shares = self.get_shares_outstanding()
        
        if price is not None and shares is not None:
            return price * shares
        
        return None
    
    def calculate_margin_of_safety(self, intrinsic_value):
        """
        Calculate margin of safety.
        
        Args:
            intrinsic_value (float): Estimated intrinsic value
            
        Returns:
            float: Margin of safety as a percentage
        """
        current_price = self.get_current_price()
        
        if current_price is not None and intrinsic_value is not None and current_price > 0:
            return (intrinsic_value - current_price) / current_price
        
        return None


class DCFModel(ValuationModel):
    """
    Discounted Cash Flow (DCF) valuation model.
    """
    
    def __init__(self, financial_data=None, market_data=None):
        """
        Initialize the DCF model.
        
        Args:
            financial_data (dict): Financial statements data
            market_data (dict): Market data
        """
        super().__init__(financial_data, market_data)
    
    def calculate_free_cash_flow(self, year_index=-1):
        """
        Calculate free cash flow from financial data.
        
        Args:
            year_index (int): Index of year to use (-1 for most recent)
            
        Returns:
            float: Free cash flow
        """
        if 'cash_flow' not in self.financial_data:
            return None
        
        cash_flow = self.financial_data['cash_flow']
        
        if isinstance(cash_flow, pd.DataFrame):
            if 'free_cash_flow' in cash_flow.columns:
                return cash_flow['free_cash_flow'].iloc[year_index]
            
            if 'operating_cash_flow' in cash_flow.columns and 'capital_expenditures' in cash_flow.columns:
                return cash_flow['operating_cash_flow'].iloc[year_index] + cash_flow['capital_expenditures'].iloc[year_index]
        
        return None
    
    def calculate_wacc(self, risk_free_rate=0.03, market_risk_premium=0.05, beta=1.0):
        """
        Calculate Weighted Average Cost of Capital.
        
        Args:
            risk_free_rate (float): Risk-free rate
            market_risk_premium (float): Market risk premium
            beta (float): Company beta
            
        Returns:
            float: WACC
        """
        if 'balance_sheet' not in self.financial_data:
            return None
        
        balance_sheet = self.financial_data['balance_sheet']
        income_stmt = self.financial_data.get('income_statement')
        
        if isinstance(balance_sheet, pd.DataFrame) and isinstance(income_stmt, pd.DataFrame):
            # Extract required values
            if 'total_debt' in balance_sheet.columns and 'total_equity' in balance_sheet.columns:
                total_debt = balance_sheet['total_debt'].iloc[-1]
                total_equity = balance_sheet['total_equity'].iloc[-1]
                
                # Calculate weights
                total_capital = total_debt + total_equity
                debt_weight = total_debt / total_capital if total_capital > 0 else 0
                equity_weight = total_equity / total_capital if total_capital > 0 else 0
                
                # Calculate cost of equity (CAPM)
                cost_of_equity = risk_free_rate + beta * market_risk_premium
                
                # Calculate cost of debt
                cost_of_debt = 0.05  # Default value
                
                if 'interest_expense' in income_stmt.columns:
                    interest_expense = income_stmt['interest_expense'].iloc[-1]
                    cost_of_debt = interest_expense / total_debt if total_debt > 0 else 0.05
                
                # Assume tax rate of 20% (Saudi corporate tax rate)
                tax_rate = 0.2
                
                # Calculate WACC
                wacc = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)
                
                return wacc
        
        # Default WACC if calculation fails
        return 0.1  # 10% as default
    
    def project_cash_flows(self, years=5, growth_rates=None, terminal_growth=0.03):
        """
        Project future cash flows.
        
        Args:
            years (int): Number of years to project
            growth_rates (list): Annual growth rates for each year
            terminal_growth (float): Terminal growth rate
            
        Returns:
            dict: Projected cash flows and terminal value
        """
        # Get base free cash flow
        base_fcf = self.calculate_free_cash_flow()
        
        if base_fcf is None:
            return None
        
        # Default growth rates if not provided
        if growth_rates is None:
            # Start with higher growth, gradually decreasing
            growth_rates = [0.15, 0.12, 0.10, 0.08, 0.06][:years]
            
            # If fewer years specified, use the last growth rate for remaining years
            if len(growth_rates) < years:
                growth_rates.extend([growth_rates[-1]] * (years - len(growth_rates)))
        
        # Project cash flows
        projected_cash_flows = []
        current_fcf = base_fcf
        
        for i in range(years):
            growth_rate = growth_rates[i] if i < len(growth_rates) else growth_rates[-1]
            current_fcf *= (1 + growth_rate)
            projected_cash_flows.append(current_fcf)
        
        # Calculate terminal value (Gordon Growth Model)
        wacc = self.calculate_wacc()
        terminal_value = projected_cash_flows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        
        return {
            'projected_cash_flows': projected_cash_flows,
            'terminal_value': terminal_value,
            'wacc': wacc,
            'growth_rates': growth_rates,
            'terminal_growth': terminal_growth
        }
    
    def calculate_intrinsic_value(self, years=5, growth_rates=None, terminal_growth=0.03):
        """
        Calculate intrinsic value using DCF model.
        
        Args:
            years (int): Number of years to project
            growth_rates (list): Annual growth rates for each year
            terminal_growth (float): Terminal growth rate
            
        Returns:
            dict: Valuation results
        """
        # Project cash flows
        projection = self.project_cash_flows(years, growth_rates, terminal_growth)
        
        if projection is None:
            return None
        
        projected_cash_flows = projection['projected_cash_flows']
        terminal_value = projection['terminal_value']
        wacc = projection['wacc']
        
        # Calculate present value of projected cash flows
        present_values = []
        
        for i, fcf in enumerate(projected_cash_flows):
            present_values.append(fcf / ((1 + wacc) ** (i + 1)))
        
        # Calculate present value of terminal value
        terminal_value_pv = terminal_value / ((1 + wacc) ** years)
        
        # Calculate enterprise value
        enterprise_value = sum(present_values) + terminal_value_pv
        
        # Adjust for debt and cash
        balance_sheet = self.financial_data.get('balance_sheet')
        
        if isinstance(balance_sheet, pd.DataFrame):
            total_debt = balance_sheet['total_debt'].iloc[-1] if 'total_debt' in balance_sheet.columns else 0
            cash_and_equivalents = balance_sheet['cash_and_equivalents'].iloc[-1] if 'cash_and_equivalents' in balance_sheet.columns else 0
            
            equity_value = enterprise_value - total_debt + cash_and_equivalents
        else:
            equity_value = enterprise_value
        
        # Calculate per share value
        shares_outstanding = self.get_shares_outstanding()
        
        if shares_outstanding:
            per_share_value = equity_value / shares_outstanding
        else:
            per_share_value = None
        
        # Calculate margin of safety
        margin_of_safety = self.calculate_margin_of_safety(per_share_value)
        
        # Compile results
        results = {
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'intrinsic_value_per_share': per_share_value,
            'current_price': self.get_current_price(),
            'margin_of_safety': margin_of_safety,
            'wacc': wacc,
            'projected_cash_flows': projected_cash_flows,
            'terminal_value': terminal_value,
            'present_value_of_cash_flows': sum(present_values),
            'present_value_of_terminal_value': terminal_value_pv,
            'growth_rates': projection['growth_rates'],
            'terminal_growth': terminal_growth
        }
        
        return results


class DividendDiscountModel(ValuationModel):
    """
    Dividend Discount Model (DDM) for valuation.
    """
    
    def __init__(self, financial_data=None, market_data=None):
        """
        Initialize the DDM model.
        
        Args:
            financial_data (dict): Financial statements data
            market_data (dict): Market data
        """
        super().__init__(financial_data, market_data)
    
    def get_current_dividend(self):
        """
        Get current annual dividend.
        
        Returns:
            float: Current annual dividend
        """
        # Try to get from market data first
        if 'dividend' in self.market_data:
            return self.market_data['dividend']
        
        # Otherwise calculate from cash flow statement
        if 'cash_flow' in self.financial_data:
            cash_flow = self.financial_data['cash_flow']
            
            if isinstance(cash_flow, pd.DataFrame) and 'dividends_paid' in cash_flow.columns:
                dividends_paid = abs(cash_flow['dividends_paid'].iloc[-1])  # Convert to positive
                shares_outstanding = self.get_shares_outstanding()
                
                if shares_outstanding:
                    return dividends_paid / shares_outstanding
        
        return None
    
    def calculate_dividend_growth_rate(self, years=5):
        """
        Calculate historical dividend growth rate.
        
        Args:
            years (int): Number of years to analyze
            
        Returns:
            float: Compound annual growth rate of dividends
        """
        if 'cash_flow' in self.financial_data:
            cash_flow = self.financial_data['cash_flow']
            
            if isinstance(cash_flow, pd.DataFrame) and 'dividends_paid' in cash_flow.columns:
                # Get dividend history
                dividend_history = cash_flow['dividends_paid'].abs()  # Convert to positive
                
                if len(dividend_history) >= years:
                    # Calculate CAGR
                    start_dividend = dividend_history.iloc[-years]
                    end_dividend = dividend_history.iloc[-1]
                    
                    if start_dividend > 0:
                        return (end_dividend / start_dividend) ** (1 / years) - 1
        
        # Default growth rate if calculation fails
        return 0.05  # 5% as default
    
    def calculate_required_return(self, risk_free_rate=0.03, market_risk_premium=0.05, beta=1.0):
        """
        Calculate required rate of return using CAPM.
        
        Args:
            risk_free_rate (float): Risk-free rate
            market_risk_premium (float): Market risk premium
            beta (float): Company beta
            
        Returns:
            float: Required rate of return
        """
        return risk_free_rate + beta * market_risk_premium
    
    def calculate_intrinsic_value(self, model='gordon', growth_rates=None, years=5, terminal_growth=0.03):
        """
        Calculate intrinsic value using dividend discount model.
        
        Args:
            model (str): 'gordon' for Gordon Growth Model, 'multi_stage' for multi-stage model
            growth_rates (list): Dividend growth rates for each stage
            years (int): Number of years for multi-stage model
            terminal_growth (float): Terminal growth rate
            
        Returns:
            dict: Valuation results
        """
        current_dividend = self.get_current_dividend()
        
        if current_dividend is None:
            return None
        
        # Calculate required return
        required_return = self.calculate_required_return()
        
        if model == 'gordon':
            # Use historical growth rate if not provided
            if growth_rates is None or len(growth_rates) == 0:
                growth_rate = self.calculate_dividend_growth_rate()
            else:
                growth_rate = growth_rates[0]
            
            # Gordon Growth Model: P = D1 / (r - g)
            next_dividend = current_dividend * (1 + growth_rate)
            
            if required_return <= growth_rate:
                # Adjust required return if it's less than or equal to growth rate
                required_return = growth_rate + 0.02
            
            intrinsic_value = next_dividend / (required_return - growth_rate)
            
            results = {
                'intrinsic_value_per_share': intrinsic_value,
                'current_price': self.get_current_price(),
                'margin_of_safety': self.calculate_margin_of_safety(intrinsic_value),
                'current_dividend': current_dividend,
                'next_dividend': next_dividend,
                'growth_rate': growth_rate,
                'required_return': required_return,
                'model': 'Gordon Growth Model'
            }
        
        else:  # multi-stage
            # Default growth rates if not provided
            if growth_rates is None:
                # Start with higher growth, gradually decreasing
                growth_rates = [0.12, 0.10, 0.08, 0.06, 0.04][:years]
                
                # If fewer years specified, use the last growth rate for remaining years
                if len(growth_rates) < years:
                    growth_rates.extend([growth_rates[-1]] * (years - len(growth_rates)))
            
            # Calculate present value of dividends during growth phase
            present_values = []
            dividend = current_dividend
            
            for i in range(years):
                growth_rate = growth_rates[i] if i < len(growth_rates) else growth_rates[-1]
                dividend *= (1 + growth_rate)
                present_values.append(dividend / ((1 + required_return) ** (i + 1)))
            
            # Calculate terminal value using Gordon Growth Model
            terminal_dividend = dividend * (1 + terminal_growth)
            
            if required_return <= terminal_growth:
                # Adjust required return if it's less than or equal to terminal growth
                required_return = terminal_growth + 0.02
            
            terminal_value = terminal_dividend / (required_return - terminal_growth)
            terminal_value_pv = terminal_value / ((1 + required_return) ** years)
            
            # Calculate intrinsic value
            intrinsic_value = sum(present_values) + terminal_value_pv
            
            results = {
                'intrinsic_value_per_share': intrinsic_value,
                'current_price': self.get_current_price(),
                'margin_of_safety': self.calculate_margin_of_safety(intrinsic_value),
                'current_dividend': current_dividend,
                'projected_dividends': [current_dividend * np.prod([1 + growth_rates[j] for j in range(i+1)]) for i in range(years)],
                'terminal_value': terminal_value,
                'present_value_of_dividends': sum(present_values),
                'present_value_of_terminal_value': terminal_value_pv,
                'growth_rates': growth_rates,
                'terminal_growth': terminal_growth,
                'required_return': required_return,
                'model': 'Multi-stage Dividend Discount Model'
            }
        
        return results


class RelativeValuation(ValuationModel):
    """
    Relative valuation using multiples.
    """
    
    def __init__(self, financial_data=None, market_data=None, peer_data=None):
        """
        Initialize the relative valuation model.
        
        Args:
            financial_data (dict): Financial statements data
            market_data (dict): Market data
            peer_data (dict): Peer companies data
        """
        super().__init__(financial_data, market_data)
        self.peer_data = peer_data or {}
    
    def set_peer_data(self, peer_data):
        """
        Set or update peer companies data.
        
        Args:
            peer_data (dict): Peer companies data
        """
        self.peer_data = peer_data
    
    def calculate_pe_ratio(self):
        """
        Calculate P/E ratio.
        
        Returns:
            float: P/E ratio
        """
        price = self.get_current_price()
        
        if price is None:
            return None
        
        if 'income_statement' in self.financial_data:
            income_stmt = self.financial_data['income_statement']
            
            if isinstance(income_stmt, pd.DataFrame):
                if 'eps_basic' in income_stmt.columns:
                    eps = income_stmt['eps_basic'].iloc[-1]
                    return price / eps if eps > 0 else None
                
                if 'net_income' in income_stmt.columns:
                    net_income = income_stmt['net_income'].iloc[-1]
                    shares_outstanding = self.get_shares_outstanding()
                    
                    if shares_outstanding:
                        eps = net_income / shares_outstanding
                        return price / eps if eps > 0 else None
        
        return None
    
    def calculate_pb_ratio(self):
        """
        Calculate P/B ratio.
        
        Returns:
            float: P/B ratio
        """
        price = self.get_current_price()
        
        if price is None:
            return None
        
        if 'balance_sheet' in self.financial_data:
            balance_sheet = self.financial_data['balance_sheet']
            
            if isinstance(balance_sheet, pd.DataFrame) and 'total_equity' in balance_sheet.columns:
                total_equity = balance_sheet['total_equity'].iloc[-1]
                shares_outstanding = self.get_shares_outstanding()
                
                if shares_outstanding and total_equity > 0:
                    book_value_per_share = total_equity / shares_outstanding
                    return price / book_value_per_share
        
        return None
    
    def calculate_ps_ratio(self):
        """
        Calculate P/S ratio.
        
        Returns:
            float: P/S ratio
        """
        price = self.get_current_price()
        
        if price is None:
            return None
        
        if 'income_statement' in self.financial_data:
            income_stmt = self.financial_data['income_statement']
            
            if isinstance(income_stmt, pd.DataFrame) and 'revenue' in income_stmt.columns:
                revenue = income_stmt['revenue'].iloc[-1]
                shares_outstanding = self.get_shares_outstanding()
                
                if shares_outstanding and revenue > 0:
                    sales_per_share = revenue / shares_outstanding
                    return price / sales_per_share
        
        return None
    
    def calculate_ev_ebitda_ratio(self):
        """
        Calculate EV/EBITDA ratio.
        
        Returns:
            float: EV/EBITDA ratio
        """
        market_cap = self.get_market_cap()
        
        if market_cap is None:
            return None
        
        if 'balance_sheet' in self.financial_data and 'income_statement' in self.financial_data:
            balance_sheet = self.financial_data['balance_sheet']
            income_stmt = self.financial_data['income_statement']
            
            if isinstance(balance_sheet, pd.DataFrame) and isinstance(income_stmt, pd.DataFrame):
                if 'total_debt' in balance_sheet.columns and 'cash_and_equivalents' in balance_sheet.columns and 'ebitda' in income_stmt.columns:
                    total_debt = balance_sheet['total_debt'].iloc[-1]
                    cash_and_equivalents = balance_sheet['cash_and_equivalents'].iloc[-1]
                    ebitda = income_stmt['ebitda'].iloc[-1]
                    
                    enterprise_value = market_cap + total_debt - cash_and_equivalents
                    
                    if ebitda > 0:
                        return enterprise_value / ebitda
        
        return None
    
    def calculate_dividend_yield(self):
        """
        Calculate dividend yield.
        
        Returns:
            float: Dividend yield
        """
        price = self.get_current_price()
        
        if price is None:
            return None
        
        current_dividend = None
        
        # Try to get from market data first
        if 'dividend' in self.market_data:
            current_dividend = self.market_data['dividend']
        
        # Otherwise calculate from cash flow statement
        elif 'cash_flow' in self.financial_data:
            cash_flow = self.financial_data['cash_flow']
            
            if isinstance(cash_flow, pd.DataFrame) and 'dividends_paid' in cash_flow.columns:
                dividends_paid = abs(cash_flow['dividends_paid'].iloc[-1])  # Convert to positive
                shares_outstanding = self.get_shares_outstanding()
                
                if shares_outstanding:
                    current_dividend = dividends_paid / shares_outstanding
        
        if current_dividend is not None and price > 0:
            return current_dividend / price
        
        return None
    
    def calculate_all_multiples(self):
        """
        Calculate all valuation multiples.
        
        Returns:
            dict: Valuation multiples
        """
        return {
            'pe_ratio': self.calculate_pe_ratio(),
            'pb_ratio': self.calculate_pb_ratio(),
            'ps_ratio': self.calculate_ps_ratio(),
            'ev_ebitda_ratio': self.calculate_ev_ebitda_ratio(),
            'dividend_yield': self.calculate_dividend_yield()
        }
    
    def calculate_peer_average_multiples(self):
        """
        Calculate average multiples for peer companies.
        
        Returns:
            dict: Average peer multiples
        """
        if not self.peer_data:
            return None
        
        # Initialize counters and sums
        multiples = {
            'pe_ratio': {'sum': 0, 'count': 0},
            'pb_ratio': {'sum': 0, 'count': 0},
            'ps_ratio': {'sum': 0, 'count': 0},
            'ev_ebitda_ratio': {'sum': 0, 'count': 0},
            'dividend_yield': {'sum': 0, 'count': 0}
        }
        
        # Sum up peer multiples
        for peer_name, peer_info in self.peer_data.items():
            for multiple, data in multiples.items():
                if multiple in peer_info and peer_info[multiple] is not None and peer_info[multiple] > 0:
                    # For P/E, P/B, P/S, EV/EBITDA, exclude extreme values
                    if multiple != 'dividend_yield' and peer_info[multiple] > 100:
                        continue
                    
                    data['sum'] += peer_info[multiple]
                    data['count'] += 1
        
        # Calculate averages
        averages = {}
        for multiple, data in multiples.items():
            if data['count'] > 0:
                averages[multiple] = data['sum'] / data['count']
            else:
                averages[multiple] = None
        
        return averages
    
    def calculate_intrinsic_value(self):
        """
        Calculate intrinsic value using relative valuation.
        
        Returns:
            dict: Valuation results
        """
        # Calculate company multiples
        company_multiples = self.calculate_all_multiples()
        
        # Calculate peer average multiples
        peer_multiples = self.calculate_peer_average_multiples()
        
        if not peer_multiples:
            return None
        
        # Calculate implied values based on each multiple
        implied_values = {}
        
        if 'income_statement' in self.financial_data and 'balance_sheet' in self.financial_data:
            income_stmt = self.financial_data['income_statement']
            balance_sheet = self.financial_data['balance_sheet']
            
            if isinstance(income_stmt, pd.DataFrame) and isinstance(balance_sheet, pd.DataFrame):
                shares_outstanding = self.get_shares_outstanding()
                
                # P/E ratio
                if 'pe_ratio' in peer_multiples and peer_multiples['pe_ratio'] is not None:
                    if 'net_income' in income_stmt.columns:
                        net_income = income_stmt['net_income'].iloc[-1]
                        if net_income > 0 and shares_outstanding:
                            eps = net_income / shares_outstanding
                            implied_values['pe_ratio'] = eps * peer_multiples['pe_ratio']
                
                # P/B ratio
                if 'pb_ratio' in peer_multiples and peer_multiples['pb_ratio'] is not None:
                    if 'total_equity' in balance_sheet.columns:
                        total_equity = balance_sheet['total_equity'].iloc[-1]
                        if total_equity > 0 and shares_outstanding:
                            book_value_per_share = total_equity / shares_outstanding
                            implied_values['pb_ratio'] = book_value_per_share * peer_multiples['pb_ratio']
                
                # P/S ratio
                if 'ps_ratio' in peer_multiples and peer_multiples['ps_ratio'] is not None:
                    if 'revenue' in income_stmt.columns:
                        revenue = income_stmt['revenue'].iloc[-1]
                        if revenue > 0 and shares_outstanding:
                            sales_per_share = revenue / shares_outstanding
                            implied_values['ps_ratio'] = sales_per_share * peer_multiples['ps_ratio']
                
                # EV/EBITDA ratio
                if 'ev_ebitda_ratio' in peer_multiples and peer_multiples['ev_ebitda_ratio'] is not None:
                    if 'ebitda' in income_stmt.columns and 'total_debt' in balance_sheet.columns and 'cash_and_equivalents' in balance_sheet.columns:
                        ebitda = income_stmt['ebitda'].iloc[-1]
                        total_debt = balance_sheet['total_debt'].iloc[-1]
                        cash_and_equivalents = balance_sheet['cash_and_equivalents'].iloc[-1]
                        
                        if ebitda > 0 and shares_outstanding:
                            enterprise_value = ebitda * peer_multiples['ev_ebitda_ratio']
                            equity_value = enterprise_value - total_debt + cash_and_equivalents
                            implied_values['ev_ebitda_ratio'] = equity_value / shares_outstanding
                
                # Dividend yield
                if 'dividend_yield' in peer_multiples and peer_multiples['dividend_yield'] is not None:
                    current_dividend = None
                    
                    # Try to get from market data first
                    if 'dividend' in self.market_data:
                        current_dividend = self.market_data['dividend']
                    
                    # Otherwise calculate from cash flow statement
                    elif 'cash_flow' in self.financial_data:
                        cash_flow = self.financial_data['cash_flow']
                        
                        if isinstance(cash_flow, pd.DataFrame) and 'dividends_paid' in cash_flow.columns:
                            dividends_paid = abs(cash_flow['dividends_paid'].iloc[-1])
                            if shares_outstanding:
                                current_dividend = dividends_paid / shares_outstanding
                    
                    if current_dividend is not None and peer_multiples['dividend_yield'] > 0:
                        implied_values['dividend_yield'] = current_dividend / peer_multiples['dividend_yield']
        
        # Calculate weighted average intrinsic value
        weights = {
            'pe_ratio': 0.3,
            'pb_ratio': 0.2,
            'ps_ratio': 0.1,
            'ev_ebitda_ratio': 0.3,
            'dividend_yield': 0.1
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for multiple, value in implied_values.items():
            if value is not None:
                weighted_sum += value * weights[multiple]
                total_weight += weights[multiple]
        
        if total_weight > 0:
            weighted_average = weighted_sum / total_weight
        else:
            weighted_average = None
        
        # Calculate margin of safety
        margin_of_safety = self.calculate_margin_of_safety(weighted_average)
        
        # Compile results
        results = {
            'intrinsic_value_per_share': weighted_average,
            'current_price': self.get_current_price(),
            'margin_of_safety': margin_of_safety,
            'company_multiples': company_multiples,
            'peer_multiples': peer_multiples,
            'implied_values': implied_values,
            'weights': weights
        }
        
        return results