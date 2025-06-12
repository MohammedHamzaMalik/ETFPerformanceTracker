import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_etf_info(symbol):
    try:
        etf = yf.Ticker(symbol)
        # Get historical data instead of info
        hist = etf.history(period="2d")
        
        if hist.empty:
            return None
            
        current_price = float(hist['Close'].iloc[-1])
        previous_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        volume = float(hist['Volume'].iloc[-1])
        
        return {
            'Name': symbol,  # Using symbol as name since info API is unreliable
            'Symbol': symbol,
            'Current Price': current_price,
            'Previous Close': previous_close,
            'Volume': volume,
            'Description': f"ETF with symbol {symbol}"  # Basic description
        }
    except Exception as e:
        print(f"Could not fetch info for {symbol}: {str(e)}")
        return None

def get_top_etfs():
    # List of common ETFs
    etf_list = ['SPY', 'QQQ', 'VTI', 'IWM', 'EFA', 'EEM', 'VNQ', 'GLD', 'TLT', 'HYG']
    
    etf_data = []
    for symbol in etf_list:
        info = get_etf_info(symbol)
        if info:
            try:
                # Calculate daily return
                daily_return = ((info['Current Price'] - info['Previous Close']) / 
                              info['Previous Close'] * 100)
                
                etf_data.append({
                    'Symbol': symbol,
                    'Price': info['Current Price'],
                    'Daily Return (%)': round(daily_return, 2),
                    'Volume': info['Volume']
                })
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                continue
    
    if not etf_data:
        return pd.DataFrame()
        
    return pd.DataFrame(etf_data)