import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class InvestmentCalculator:
    def __init__(self):
        pass
    
    def calculate_investment_growth(self, symbol, initial_investment):
        """Calculate how an investment would have grown since inception"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get maximum historical data
            hist = ticker.history(period="max")
            
            if hist.empty:
                return None
            
            # Get first and last prices
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            
            # Calculate dates and years
            start_date = hist.index[0]
            end_date = hist.index[-1]
            years = (end_date - start_date).days / 365.25
            
            # Calculate investment growth
            price_multiplier = last_price / first_price
            current_value = initial_investment * price_multiplier
            total_return = ((current_value / initial_investment) - 1) * 100
            
            # Calculate CAGR
            cagr = ((current_value / initial_investment) ** (1/years) - 1) * 100
            
            # Create growth data for charting
            growth_data = self._create_growth_chart_data(hist, initial_investment, first_price)
            
            return {
                'symbol': symbol,
                'initial_investment': initial_investment,
                'current_value': current_value,
                'total_return': total_return,
                'cagr': cagr,
                'years': years,
                'start_date': start_date.date(),
                'end_date': end_date.date(),
                'growth_data': growth_data
            }
            
        except Exception as e:
            st.error(f"Error calculating investment growth for {symbol}: {str(e)}")
            return None
    
    def _create_growth_chart_data(self, hist, initial_investment, first_price):
        """Create data for growth chart visualization"""
        try:
            # Sample data points for chart (monthly intervals to avoid too many points)
            if len(hist) > 60:  # More than 60 days of data
                # Sample every month approximately
                sample_interval = max(1, len(hist) // 60)
                sampled_hist = hist.iloc[::sample_interval].copy()
            else:
                sampled_hist = hist.copy()
            
            # Calculate portfolio value over time
            sampled_hist['Portfolio_Value'] = (sampled_hist['Close'] / first_price) * initial_investment
            
            # Prepare data for plotly
            chart_data = pd.DataFrame({
                'Date': sampled_hist.index,
                'Portfolio_Value': sampled_hist['Portfolio_Value']
            })
            
            return chart_data
            
        except Exception as e:
            st.warning(f"Could not create chart data: {str(e)}")
            return None
    
    def quick_calculation(self, symbol, amount):
        """Quick calculation for display purposes"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="max")
            
            if hist.empty:
                return None
            
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            
            current_value = amount * (last_price / first_price)
            
            return {
                'current_value': current_value,
                'multiplier': last_price / first_price
            }
            
        except Exception as e:
            return None
    
    def compare_etfs(self, etf1, etf2, investment_amount):
        """Compare two ETFs performance"""
        try:
            results = {}
            
            for symbol in [etf1, etf2]:
                result = self.calculate_investment_growth(symbol, investment_amount)
                if result:
                    results[symbol] = result
            
            return results if len(results) == 2 else None
            
        except Exception as e:
            st.error(f"Error comparing ETFs: {str(e)}")
            return None
    
    def calculate_future_value(self, principal, annual_rate, years, monthly_contribution=0):
        """Calculate future value with compound interest and optional monthly contributions"""
        try:
            # Monthly interest rate
            monthly_rate = annual_rate / 100 / 12
            months = years * 12
            
            # Future value of initial principal
            fv_principal = principal * ((1 + monthly_rate) ** months)
            
            # Future value of monthly contributions (annuity)
            if monthly_contribution > 0:
                fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                fv_contributions = 0
            
            total_fv = fv_principal + fv_contributions
            total_invested = principal + (monthly_contribution * months)
            total_gain = total_fv - total_invested
            
            return {
                'future_value': total_fv,
                'total_invested': total_invested,
                'total_gain': total_gain,
                'gain_percentage': (total_gain / total_invested) * 100 if total_invested > 0 else 0
            }
            
        except Exception as e:
            st.error(f"Error calculating future value: {str(e)}")
            return None
    
    def calculate_required_investment(self, target_value, annual_rate, years):
        """Calculate required initial investment to reach target value"""
        try:
            # Present value calculation
            monthly_rate = annual_rate / 100 / 12
            months = years * 12
            
            required_investment = target_value / ((1 + monthly_rate) ** months)
            
            return {
                'required_investment': required_investment,
                'target_value': target_value,
                'annual_rate': annual_rate,
                'years': years
            }
            
        except Exception as e:
            st.error(f"Error calculating required investment: {str(e)}")
            return None
    
    def get_risk_metrics(self, symbol, period="2y"):
        """Calculate risk metrics for an ETF"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Calculate daily returns
            daily_returns = hist['Close'].pct_change().dropna()
            
            # Risk metrics
            volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized volatility
            max_drawdown = self._calculate_max_drawdown(hist['Close'])
            sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
            
            return {
                'volatility': round(volatility, 2),
                'max_drawdown': round(max_drawdown, 2),
                'sharpe_ratio': round(sharpe_ratio, 2)
            }
            
        except Exception as e:
            st.warning(f"Could not calculate risk metrics for {symbol}: {str(e)}")
            return None
    
    def _calculate_max_drawdown(self, prices):
        """Calculate maximum drawdown"""
        try:
            # Calculate running maximum
            peak = prices.expanding().max()
            # Calculate drawdown
            drawdown = (prices - peak) / peak * 100
            # Return maximum drawdown (most negative value)
            return drawdown.min()
        except:
            return 0
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        try:
            excess_returns = returns.mean() * 252 - risk_free_rate  # Annualized excess return
            volatility = returns.std() * np.sqrt(252)  # Annualized volatility
            
            if volatility == 0:
                return 0
            
            return excess_returns / volatility
        except:
            return 0
