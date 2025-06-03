import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class ETFAnalyzer:
    def __init__(self):
        # Global ETF database organized by country and region
        self.global_etf_database = {
            # United States
            'USA': {
                'SPY': 'SPDR S&P 500 ETF Trust',
                'VOO': 'Vanguard S&P 500 ETF',
                'IVV': 'iShares Core S&P 500 ETF',
                'VTI': 'Vanguard Total Stock Market ETF',
                'QQQ': 'Invesco QQQ Trust',
                'VGT': 'Vanguard Information Technology ETF',
                'XLK': 'Technology Select Sector SPDR Fund',
                'IWM': 'iShares Russell 2000 ETF',
                'VB': 'Vanguard Small-Cap ETF',
                'BND': 'Vanguard Total Bond Market ETF',
                'AGG': 'iShares Core U.S. Aggregate Bond ETF',
                'TLT': 'iShares 20+ Year Treasury Bond ETF',
                'HYG': 'iShares iBoxx High Yield Corporate Bond ETF',
                'VNQ': 'Vanguard Real Estate ETF',
                'GLD': 'SPDR Gold Shares',
                'XLF': 'Financial Select Sector SPDR Fund',
                'XLE': 'Energy Select Sector SPDR Fund',
                'XLV': 'Health Care Select Sector SPDR Fund',
                'VYM': 'Vanguard High Dividend Yield ETF',
                'SCHD': 'Schwab US Dividend Equity ETF'
            },
            
            # Canada
            'CANADA': {
                'XIU.TO': 'iShares Core S&P/TSX Capped Composite Index ETF',
                'VFV.TO': 'Vanguard S&P 500 Index ETF',
                'VCN.TO': 'Vanguard FTSE Canada All Cap Index ETF',
                'VTI.TO': 'Vanguard Total Stock Market Index ETF',
                'VGRO.TO': 'Vanguard Growth ETF Portfolio',
                'VBAL.TO': 'Vanguard Balanced ETF Portfolio'
            },
            
            # Europe - UK
            'UK': {
                'VUSA.L': 'Vanguard S&P 500 UCITS ETF',
                'VWRL.L': 'Vanguard FTSE All-World UCITS ETF',
                'VUKE.L': 'Vanguard FTSE 100 UCITS ETF',
                'ISF.L': 'iShares Core S&P 500 UCITS ETF',
                'IWDA.L': 'iShares Core MSCI World UCITS ETF'
            },
            
            # Europe - Germany
            'GERMANY': {
                'EXS1.DE': 'iShares Core DAX UCITS ETF',
                'EXXT.DE': 'iShares Core EURO STOXX 50 UCITS ETF',
                'IWDA.DE': 'iShares Core MSCI World UCITS ETF',
                'VWCE.DE': 'Vanguard FTSE All-World UCITS ETF'
            },
            
            # Asia Pacific - Japan
            'JAPAN': {
                'EWJ': 'iShares MSCI Japan ETF',
                '1306.T': 'TOPIX ETF',
                '1321.T': 'Nikkei 225 ETF',
                'DXJ': 'WisdomTree Japan Hedged Equity Fund'
            },
            
            # Asia Pacific - Australia
            'AUSTRALIA': {
                'VAS.AX': 'Vanguard Australian Shares Index ETF',
                'IOZ.AX': 'iShares Core S&P/ASX 200 ETF',
                'VGS.AX': 'Vanguard MSCI Index International Shares ETF',
                'IVV.AX': 'iShares Core S&P 500 ETF'
            },
            
            # Asia - China
            'CHINA': {
                'FXI': 'iShares China Large-Cap ETF',
                'MCHI': 'iShares MSCI China ETF',
                'ASHR': 'Xtrackers Harvest CSI 300 China A-Shares ETF',
                'KWEB': 'KraneShares CSI China Internet ETF'
            },
            
            # Asia - India
            'INDIA': {
                'INDA': 'iShares MSCI India ETF',
                'INDY': 'iShares MSCI India Small-Cap ETF',
                'EPI': 'WisdomTree India Earnings Fund'
            },
            
            # International
            'INTERNATIONAL': {
                'EFA': 'iShares MSCI EAFE ETF',
                'VEA': 'Vanguard FTSE Developed Markets ETF',
                'EEM': 'iShares MSCI Emerging Markets ETF',
                'VWO': 'Vanguard FTSE Emerging Markets ETF',
                'IEFA': 'iShares Core MSCI EAFE IMI Index ETF'
            }
        }
        
        # Create a flattened version for backward compatibility
        self.extended_etf_list = {}
        for country, etfs in self.global_etf_database.items():
            self.extended_etf_list.update(etfs)
    
    def get_etf_info(self, symbol):
        """Get basic ETF information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'name': info.get('longName', self.extended_etf_list.get(symbol, 'Unknown')),
                'expense_ratio': info.get('annualReportExpenseRatio', 0.005),
                'aum': info.get('totalAssets', 0),
                'inception_date': info.get('fundInceptionDate', None)
            }
        except Exception as e:
            return {
                'symbol': symbol,
                'name': self.extended_etf_list.get(symbol, 'Unknown'),
                'expense_ratio': 0.005,
                'aum': 0,
                'inception_date': None
            }
    
    def calculate_cagr(self, symbol, start_date=None):
        """Calculate CAGR from inception or specified start date"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            if start_date:
                hist = ticker.history(start=start_date)
            else:
                hist = ticker.history(period="max")
            
            if hist.empty or len(hist) < 2:
                return None, None, None
            
            # Get first and last prices
            first_price = hist['Close'].iloc[0]
            last_price = hist['Close'].iloc[-1]
            
            # Calculate number of years
            start_date_ts = hist.index[0]
            end_date_ts = hist.index[-1]
            years = (end_date_ts - start_date_ts).days / 365.25
            
            if years <= 0:
                return None, None, None
            
            # Calculate CAGR
            cagr = ((last_price / first_price) ** (1/years) - 1) * 100
            
            return cagr, start_date_ts.date(), years
            
        except Exception as e:
            return None, None, None
    
    def get_top_etfs(self, country_filter=None):
        """Get top performing ETFs with their metrics"""
        results = []
        
        # Determine which ETFs to analyze
        if country_filter and country_filter != "All Countries":
            etf_dict = self.global_etf_database.get(country_filter, {})
        else:
            etf_dict = self.extended_etf_list
        
        if not etf_dict:
            return pd.DataFrame()
        
        progress_bar = st.progress(0)
        total_etfs = len(etf_dict)
        
        for i, (symbol, name) in enumerate(list(etf_dict.items())[:10]):  # Limit to 10 for demo
            try:
                progress_bar.progress((i + 1) / min(10, total_etfs))
                
                # Get ETF info
                etf_info = self.get_etf_info(symbol)
                if not etf_info:
                    continue
                
                # Calculate CAGR
                cagr, inception_date, years = self.calculate_cagr(symbol)
                if cagr is None:
                    continue
                
                # Prepare data
                expense_ratio_pct = etf_info['expense_ratio'] * 100 if etf_info['expense_ratio'] else 0.5
                aum_billions = etf_info['aum'] / 1e9 if etf_info['aum'] and etf_info['aum'] > 0 else 0
                
                result = {
                    'Symbol': symbol,
                    'Name': etf_info['name'],
                    'CAGR (%)': round(cagr, 2),
                    'Inception Date': inception_date if inception_date else 'Unknown',
                    'Years': round(years, 1),
                    'Expense Ratio (%)': round(expense_ratio_pct, 3),
                    'AUM (Billions)': f"${aum_billions:.1f}B" if aum_billions > 0 else 'N/A'
                }
                
                results.append(result)
                
            except Exception as e:
                continue
        
        progress_bar.empty()
        
        if not results:
            return pd.DataFrame()
        
        # Create DataFrame and sort by CAGR
        df = pd.DataFrame(results)
        df = df.sort_values('CAGR (%)', ascending=False)
        
        return df
    
    def get_available_countries(self):
        """Get list of available countries"""
        return list(self.global_etf_database.keys())
    
    def get_etfs_by_country(self, country):
        """Get ETFs filtered by country"""
        return self.global_etf_database.get(country, {})
    
    def search_etf_by_country(self, search_term, country=None):
        """Search for ETFs by symbol or name, optionally filtered by country"""
        search_term = search_term.upper().strip()
        results = []
        
        # If country is specified, search only in that country
        if country and country in self.global_etf_database:
            etf_dict = self.global_etf_database[country]
        else:
            etf_dict = self.extended_etf_list
        
        for symbol, name in etf_dict.items():
            if (search_term in symbol.upper() or 
                search_term in name.upper()):
                
                # Find which country this ETF belongs to
                etf_country = "Unknown"
                for c, etfs in self.global_etf_database.items():
                    if symbol in etfs:
                        etf_country = c
                        break
                
                results.append({
                    'symbol': symbol, 
                    'name': name,
                    'country': etf_country
                })
        
        return results
    
    def get_all_etfs(self):
        """Get all available ETFs for selection"""
        return self.extended_etf_list
    
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
            volatility = hist['Close'].pct_change().std() * np.sqrt(252) * 100
            
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
                'expense_ratio': (info.get('annualReportExpenseRatio', 0.005) * 100),
                'aum': info.get('totalAssets', 0)
            }
            
            return summary
            
        except Exception as e:
            return None