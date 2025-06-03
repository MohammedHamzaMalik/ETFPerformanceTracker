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
        
        # Global ETF database organized by country and region
        self.global_etf_database = {
            # United States
            'USA': {
                # Large Cap US
                'SPY': 'SPDR S&P 500 ETF Trust',
                'VOO': 'Vanguard S&P 500 ETF',
                'IVV': 'iShares Core S&P 500 ETF',
                'VTI': 'Vanguard Total Stock Market ETF',
                'ITOT': 'iShares Core S&P Total US Stock Market ETF',
                'SCHX': 'Schwab US Large-Cap ETF',
                'SCHA': 'Schwab US Small-Cap ETF',
                'SCHM': 'Schwab US Mid-Cap ETF',
                'SCHB': 'Schwab US Broad Market ETF',
                
                # Technology
                'QQQ': 'Invesco QQQ Trust',
                'VGT': 'Vanguard Information Technology ETF',
                'XLK': 'Technology Select Sector SPDR Fund',
                'FTEC': 'Fidelity MSCI Information Technology ETF',
                'SOXX': 'iShares Semiconductor ETF',
                'IGV': 'iShares Expanded Tech-Software Sector ETF',
                'ARKK': 'ARK Innovation ETF',
                'ARKQ': 'ARK Autonomous Technology & Robotics ETF',
                
                # Small Cap
                'IWM': 'iShares Russell 2000 ETF',
                'VB': 'Vanguard Small-Cap ETF',
                'VTWO': 'Vanguard Russell 2000 ETF',
                'IJR': 'iShares Core S&P Small-Cap ETF',
                
                # Bonds
                'BND': 'Vanguard Total Bond Market ETF',
                'AGG': 'iShares Core U.S. Aggregate Bond ETF',
                'TLT': 'iShares 20+ Year Treasury Bond ETF',
                'HYG': 'iShares iBoxx High Yield Corporate Bond ETF',
                'LQD': 'iShares iBoxx Investment Grade Corporate Bond ETF',
                'SCHZ': 'Schwab Intermediate-Term Treasury ETF',
                'VTEB': 'Vanguard Tax-Exempt Bond ETF',
                
                # Real Estate
                'VNQ': 'Vanguard Real Estate ETF',
                'SCHH': 'Schwab U.S. REIT ETF',
                'IYR': 'iShares U.S. Real Estate ETF',
                'XLRE': 'Real Estate Select Sector SPDR Fund',
                
                # Commodities
                'GLD': 'SPDR Gold Shares',
                'SLV': 'iShares Silver Trust',
                'DBC': 'Invesco DB Commodity Index Tracking Fund',
                'USO': 'United States Oil Fund',
                'PDBC': 'Invesco Optimum Yield Diversified Commodity Strategy No K-1 ETF',
                
                # Sector ETFs
                'XLF': 'Financial Select Sector SPDR Fund',
                'XLE': 'Energy Select Sector SPDR Fund',
                'XLV': 'Health Care Select Sector SPDR Fund',
                'XLI': 'Industrial Select Sector SPDR Fund',
                'XLY': 'Consumer Discretionary Select Sector SPDR Fund',
                'XLP': 'Consumer Staples Select Sector SPDR Fund',
                'XLU': 'Utilities Select Sector SPDR Fund',
                'XLB': 'Materials Select Sector SPDR Fund',
                
                # Dividend ETFs
                'VYM': 'Vanguard High Dividend Yield ETF',
                'SCHD': 'Schwab US Dividend Equity ETF',
                'DVY': 'iShares Select Dividend ETF',
                'HDV': 'iShares High Dividend ETF',
                'NOBL': 'ProShares S&P 500 Dividend Aristocrats ETF',
                'DGRO': 'iShares Core Dividend Growth ETF'
            },
            
            # Canada
            'CANADA': {
                'VTI.TO': 'Vanguard Total Stock Market Index ETF',
                'VFV.TO': 'Vanguard S&P 500 Index ETF',
                'VCN.TO': 'Vanguard FTSE Canada All Cap Index ETF',
                'TDB902.TO': 'TD Canadian Index Fund',
                'XIU.TO': 'iShares Core S&P/TSX Capped Composite Index ETF',
                'VBR.TO': 'Vanguard Canadian Aggregate Bond Index ETF',
                'VSP.TO': 'Vanguard S&P 500 Index ETF',
                'VEA.TO': 'Vanguard FTSE Developed Markets ETF',
                'VGRO.TO': 'Vanguard Growth ETF Portfolio',
                'VBAL.TO': 'Vanguard Balanced ETF Portfolio'
            },
            
            # Europe - UK
            'UK': {
                'VUSA.L': 'Vanguard S&P 500 UCITS ETF',
                'VWRL.L': 'Vanguard FTSE All-World UCITS ETF',
                'VMID.L': 'Vanguard FTSE 250 UCITS ETF',
                'VUKE.L': 'Vanguard FTSE 100 UCITS ETF',
                'VERX.L': 'Vanguard FTSE Emerging Markets UCITS ETF',
                'VHYL.L': 'Vanguard FTSE All-World High Dividend Yield UCITS ETF',
                'VGOV.L': 'Vanguard UK Government Bond UCITS ETF',
                'ISF.L': 'iShares Core S&P 500 UCITS ETF',
                'IWDA.L': 'iShares Core MSCI World UCITS ETF',
                'IUKD.L': 'iShares Core FTSE 100 UCITS ETF'
            },
            
            # Europe - Germany
            'GERMANY': {
                'EXS1.DE': 'iShares Core DAX UCITS ETF',
                'EXXT.DE': 'iShares Core EURO STOXX 50 UCITS ETF',
                'EUNL.DE': 'iShares Core MSCI Europe UCITS ETF',
                'IWDA.DE': 'iShares Core MSCI World UCITS ETF',
                'VWCE.DE': 'Vanguard FTSE All-World UCITS ETF',
                'VUSA.DE': 'Vanguard S&P 500 UCITS ETF',
                'A1JX52.DE': 'Vanguard FTSE All-World UCITS ETF',
                'DBX1MW.DE': 'Xtrackers MSCI World UCITS ETF',
                'LYX0YD.DE': 'Lyxor EURO STOXX 50 (DR) UCITS ETF'
            },
            
            # Europe - France
            'FRANCE': {
                'CW8.PA': 'iShares Core MSCI World UCITS ETF',
                'CAC.PA': 'Lyxor CAC 40 (DR) UCITS ETF',
                'EWQ': 'iShares MSCI France ETF',
                'EWGS.PA': 'iShares MSCI EMU Large Cap UCITS ETF',
                'EWQS.PA': 'iShares Edge MSCI Europe Quality Factor UCITS ETF'
            },
            
            # Asia Pacific - Japan
            'JAPAN': {
                'EWJ': 'iShares MSCI Japan ETF',
                '1306.T': 'TOPIX ETF',
                '1321.T': 'Nikkei 225 ETF',
                'VEA': 'Vanguard FTSE Developed Markets ETF (includes Japan)',
                'IEFA': 'iShares Core MSCI EAFE ETF (includes Japan)',
                'DXJ': 'WisdomTree Japan Hedged Equity Fund',
                'JPXN': 'iShares JPX-Nikkei 400 ETF',
                'HEWJ': 'iShares Currency Hedged MSCI Japan ETF'
            },
            
            # Asia Pacific - Australia
            'AUSTRALIA': {
                'VAS.AX': 'Vanguard Australian Shares Index ETF',
                'IOZ.AX': 'iShares Core S&P/ASX 200 ETF',
                'VGS.AX': 'Vanguard MSCI Index International Shares ETF',
                'IVV.AX': 'iShares Core S&P 500 ETF',
                'VTS.AX': 'Vanguard US Total Market Shares Index ETF',
                'VAE.AX': 'Vanguard FTSE Emerging Markets Shares ETF',
                'VGB.AX': 'Vanguard Australian Government Bond Index ETF',
                'VDHG.AX': 'Vanguard Diversified High Growth Index ETF'
            },
            
            # Asia - China/Hong Kong
            'CHINA': {
                'FXI': 'iShares China Large-Cap ETF',
                'MCHI': 'iShares MSCI China ETF',
                'ASHR': 'Xtrackers Harvest CSI 300 China A-Shares ETF',
                'KWEB': 'KraneShares CSI China Internet ETF',
                'GXC': 'SPDR S&P China ETF',
                'YINN': 'Direxion Daily FTSE China Bull 3X Shares',
                '2800.HK': 'Tracker Fund of Hong Kong',
                '3040.HK': 'iShares MSCI Asia ex Japan ETF'
            },
            
            # Asia - India
            'INDIA': {
                'INDA': 'iShares MSCI India ETF',
                'INDY': 'iShares MSCI India Small-Cap ETF',
                'MINDX': 'iShares MSCI India ETF',
                'EPI': 'WisdomTree India Earnings Fund',
                'SCIN': 'Schwab Fundamental Emerging Markets Large Company Index ETF'
            },
            
            # Asia - South Korea
            'SOUTH_KOREA': {
                'EWY': 'iShares MSCI South Korea ETF',
                'FLKR': 'Franklin FTSE South Korea ETF'
            },
            
            # Emerging Markets
            'EMERGING_MARKETS': {
                'EEM': 'iShares MSCI Emerging Markets ETF',
                'VWO': 'Vanguard FTSE Emerging Markets ETF',
                'IEMG': 'iShares Core MSCI Emerging Markets IMI Index ETF',
                'SPEM': 'SPDR Portfolio Emerging Markets ETF',
                'SCHE': 'Schwab Emerging Markets Equity ETF'
            },
            
            # International Developed Markets
            'INTERNATIONAL_DEVELOPED': {
                'EFA': 'iShares MSCI EAFE ETF',
                'VEA': 'Vanguard FTSE Developed Markets ETF',
                'IEFA': 'iShares Core MSCI EAFE IMI Index ETF',
                'SCHF': 'Schwab International Equity ETF',
                'VTEB': 'Vanguard Tax-Exempt Bond ETF',
                'VXUS': 'Vanguard Total International Stock ETF'
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
                expense_ratio_pct = etf_info['expense_ratio'] * 100 if etf_info['expense_ratio'] and etf_info['expense_ratio'] is not None else 0.5
                aum_billions = round(etf_info['aum'] / 1e9, 1) if etf_info['aum'] and etf_info['aum'] is not None else 'N/A'
                
                result = {
                    'Symbol': symbol,
                    'Name': etf_info['name'],
                    'CAGR (%)': round(cagr, 2),
                    'Inception Date': inception_date.strftime('%Y-%m-%d') if inception_date else 'Unknown',
                    'Years': round(years, 1),
                    'Expense Ratio (%)': expense_ratio_pct,
                    'AUM (Billions)': aum_billions
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
    
    def search_etf(self, search_term):
        """Search for ETFs by symbol or name"""
        search_term = search_term.upper().strip()
        results = []
        
        for symbol, name in self.extended_etf_list.items():
            if (search_term in symbol.upper() or 
                search_term in name.upper()):
                results.append({'symbol': symbol, 'name': name})
        
        return results
    
    def get_all_etfs(self):
        """Get all available ETFs for selection"""
        return self.extended_etf_list
    
    def get_etfs_by_country(self, country):
        """Get ETFs filtered by country"""
        return self.global_etf_database.get(country, {})
    
    def get_available_countries(self):
        """Get list of available countries"""
        return list(self.global_etf_database.keys())
    
    def search_etf_by_country(self, search_term, country=None):
        """Search for ETFs by symbol or name, optionally filtered by country"""
        search_term = search_term.upper().strip()
        results = []
        
        # If country is specified, search only in that country
        if country and country in self.global_etf_database:
            etf_dict = self.global_etf_database[country]
            country_name = country
        else:
            # Search in all countries
            etf_dict = self.extended_etf_list
            country_name = "All Countries"
        
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
