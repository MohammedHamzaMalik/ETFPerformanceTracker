import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class ETFAnalyzer:
    def __init__(self):
        # Popular ETFs to analyze
        self.etf_list = {
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust',
            'VTI': 'Vanguard Total Stock Market ETF',
            'IWM': 'iShares Russell 2000 ETF',
            'EFA': 'iShares MSCI EAFE ETF',
            'EEM': 'iShares MSCI Emerging Markets ETF',
            'VNQ': 'Vanguard Real Estate ETF',
            'GLD': 'SPDR Gold Shares',
            'TLT': 'iShares 20+ Year Treasury Bond ETF',
            'HYG': 'iShares iBoxx High Yield Corporate Bond ETF'
        }
    
    def get_etf_info(self, symbol):
        """Get basic ETF information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', self.etf_list.get(symbol, 'Unknown')),
                'expense_ratio': info.get('annualReportExpenseRatio', None),
                'aum': info.get('totalAssets', None),
                'inception_date': info.get('fundInceptionDate', None)
            }
        except Exception as e:
            st.warning(f"Could not fetch info for {symbol}: {str(e)}")
            return None
    
    def calculate_cagr(self, symbol, start_date=None):
        """Calculate CAGR from inception or specified start date"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            if start_date:
                hist = ticker.history(start=start_date)
            else:
                # Get maximum available history
                hist = ticker.history(period="max")
            
            if hist.empty:
                return None, None, None
            
            # Get first and last prices
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            
            # Calculate number of years
            start_date = hist.index[0]
            end_date = hist.index[-1]
            years = (end_date - start_date).days / 365.25
            
            if years <= 0:
                return None, None, None
            
            # Calculate CAGR
            cagr = ((last_price / first_price) ** (1/years) - 1) * 100
            
            return cagr, start_date.date(), years
            
        except Exception as e:
            st.warning(f"Could not calculate CAGR for {symbol}: {str(e)}")
            return None, None, None
    
    def get_top_etfs(self):
        """Get top performing ETFs with their metrics"""
        results = []
        
        progress_bar = st.progress(0)
        total_etfs = len(self.etf_list)
        
        for i, (symbol, name) in enumerate(self.etf_list.items()):
            try:
                # Update progress
                progress_bar.progress((i + 1) / total_etfs)
                
                # Get ETF info
                etf_info = self.get_etf_info(symbol)
                if not etf_info:
                    continue
                
                # Calculate CAGR
                cagr, inception_date, years = self.calculate_cagr(symbol)
                if cagr is None:
                    continue
                
                # Prepare data
                result = {
                    'Symbol': symbol,
                    'Name': etf_info['name'],
                    'CAGR (%)': round(cagr, 2),
                    'Inception Date': inception_date.strftime('%Y-%m-%d') if inception_date else 'Unknown',
                    'Years': round(years, 1),
                    'Expense Ratio (%)': etf_info['expense_ratio'] * 100 if etf_info['expense_ratio'] else 0.5,
                    'AUM (Billions)': round(etf_info['aum'] / 1e9, 1) if etf_info['aum'] else 'N/A'
                }
                
                results.append(result)
                
            except Exception as e:
                st.warning(f"Error processing {symbol}: {str(e)}")
                continue
        
        progress_bar.empty()
        
        if not results:
            return pd.DataFrame()
        
        # Create DataFrame and sort by CAGR
        df = pd.DataFrame(results)
        df = df.sort_values('CAGR (%)', ascending=False)
        
        return df
    
    def get_historical_data(self, symbol, period="max"):
        """Get historical price data for an ETF"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            st.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_etf_summary(self, symbol):
        """Get comprehensive ETF summary"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return None
            
            # Calculate additional metrics
            current_price = hist['Close'].iloc[-1]
            year_high = hist['High'].max()
            year_low = hist['Low'].min()
            volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
            
            # Calculate 1-year return
            year_return = ((current_price / hist['Close'].iloc[0]) - 1) * 100
            
            summary = {
                'symbol': symbol,
                'name': info.get('longName', 'Unknown'),
                'current_price': round(current_price, 2),
                'year_high': round(year_high, 2),
                'year_low': round(year_low, 2),
                'year_return': round(year_return, 2),
                'volatility': round(volatility, 2),
                'volume': info.get('averageVolume', 'N/A'),
                'expense_ratio': info.get('annualReportExpenseRatio', 0.005) * 100,
                'aum': info.get('totalAssets', 0)
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Error getting summary for {symbol}: {str(e)}")
            return None
