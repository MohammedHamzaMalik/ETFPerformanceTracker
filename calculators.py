import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class InvestmentCalculator:
    def __init__(self):
        pass
    
    def calculate_investment_growth(self, symbol, initial_investment, include_expense_ratio=True):
        """Calculate how an investment would have grown since inception, including expense ratio impact"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get maximum historical data and ETF info
            hist = ticker.history(period="max")
            info = ticker.info
            
            if hist.empty:
                return None
            
            # Get expense ratio
            expense_ratio = info.get('annualReportExpenseRatio', 0.005)  # Default to 0.5% if not available
            
            # Get first and last prices
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            
            # Calculate dates and years
            start_date = hist.index[0]
            end_date = hist.index[-1]
            years = (end_date - start_date).days / 365.25
            
            # Calculate investment growth WITHOUT expense ratio (gross returns)
            price_multiplier = last_price / first_price
            gross_current_value = initial_investment * price_multiplier
            gross_total_return = ((gross_current_value / initial_investment) - 1) * 100
            gross_cagr = ((gross_current_value / initial_investment) ** (1/years) - 1) * 100
            
            # Calculate investment growth WITH expense ratio (net returns)
            if include_expense_ratio and expense_ratio > 0:
                # Apply expense ratio compound reduction over the years
                expense_multiplier = (1 - expense_ratio) ** years
                net_current_value = gross_current_value * expense_multiplier
                net_total_return = ((net_current_value / initial_investment) - 1) * 100
                net_cagr = ((net_current_value / initial_investment) ** (1/years) - 1) * 100
                
                # Calculate total fees paid
                total_fees = gross_current_value - net_current_value
            else:
                net_current_value = gross_current_value
                net_total_return = gross_total_return
                net_cagr = gross_cagr
                total_fees = 0
            
            # Create growth data for charting (including expense ratio impact)
            growth_data = self._create_growth_chart_data(hist, initial_investment, first_price, expense_ratio if include_expense_ratio else 0)
            
            return {
                'symbol': symbol,
                'initial_investment': initial_investment,
                'gross_current_value': gross_current_value,
                'net_current_value': net_current_value,
                'current_value': net_current_value,  # Default to net value
                'gross_total_return': gross_total_return,
                'net_total_return': net_total_return,
                'total_return': net_total_return,  # Default to net return
                'gross_cagr': gross_cagr,
                'net_cagr': net_cagr,
                'cagr': net_cagr,  # Default to net CAGR
                'expense_ratio': expense_ratio * 100,  # Convert to percentage
                'total_fees': total_fees,
                'years': years,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'growth_data': growth_data
            }
            
        except Exception as e:
            st.error(f"Error calculating investment growth for {symbol}: {str(e)}")
            return None
    
    def _create_growth_chart_data(self, hist, initial_investment, first_price, expense_ratio=0):
        """Create data for growth chart visualization with expense ratio impact"""
        try:
            # Sample data points for chart (monthly intervals to avoid too many points)
            if len(hist) > 60:  # More than 60 days of data
                # Sample every month approximately
                sample_interval = max(1, len(hist) // 60)
                sampled_hist = hist.iloc[::sample_interval].copy()
            else:
                sampled_hist = hist.copy()
            
            # Calculate portfolio value over time (gross returns)
            sampled_hist['Gross_Portfolio_Value'] = (sampled_hist['Close'] / first_price) * initial_investment
            
            # Calculate portfolio value with expense ratio impact
            if expense_ratio > 0:
                # Calculate years elapsed for each data point
                start_date = sampled_hist.index[0]
                sampled_hist['Years_Elapsed'] = [(date - start_date).days / 365.25 for date in sampled_hist.index]
                
                # Apply compound expense ratio reduction
                sampled_hist['Net_Portfolio_Value'] = (
                    sampled_hist['Gross_Portfolio_Value'] * 
                    ((1 - expense_ratio) ** sampled_hist['Years_Elapsed'])
                )
            else:
                sampled_hist['Net_Portfolio_Value'] = sampled_hist['Gross_Portfolio_Value']
            
            # Prepare data for plotly
            chart_data = pd.DataFrame({
                'Date': sampled_hist.index,
                'Gross_Portfolio_Value': sampled_hist['Gross_Portfolio_Value'],
                'Portfolio_Value': sampled_hist['Net_Portfolio_Value']  # Net value after fees
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
