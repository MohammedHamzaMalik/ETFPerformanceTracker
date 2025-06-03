import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Global ETF Performance Analyzer - Best ETFs Worldwide | Investment Returns Calculator",
    page_icon="🌍",
    layout="wide"
)

# SEO-optimized headers and content
st.title("🌍 Global ETF Performance Analyzer")
st.markdown("**Find the Best ETFs Worldwide | Calculate Investment Returns | Compare Global ETF Performance**")

# SEO meta content
st.markdown("""
<meta name="description" content="Global ETF Performance Analyzer - Find best performing ETFs from USA, Europe, Asia, and worldwide. Calculate investment returns with real-time data and expense ratio impact.">
<meta name="keywords" content="ETF performance, best ETFs worldwide, ETF calculator, investment returns, global ETFs, ETF comparison, CAGR calculator, expense ratio, ETF analysis, international ETFs">
""", unsafe_allow_html=True)

# Global ETF Database
GLOBAL_ETF_DATABASE = {
    'USA': {
        'SPY': 'SPDR S&P 500 ETF Trust',
        'VOO': 'Vanguard S&P 500 ETF',
        'QQQ': 'Invesco QQQ Trust',
        'VTI': 'Vanguard Total Stock Market ETF',
        'IWM': 'iShares Russell 2000 ETF',
        'BND': 'Vanguard Total Bond Market ETF',
        'VNQ': 'Vanguard Real Estate ETF',
        'GLD': 'SPDR Gold Shares',
        'XLK': 'Technology Select Sector SPDR Fund',
        'VYM': 'Vanguard High Dividend Yield ETF'
    },
    'CANADA': {
        'XIU.TO': 'iShares Core S&P/TSX Capped Composite Index ETF',
        'VFV.TO': 'Vanguard S&P 500 Index ETF',
        'VCN.TO': 'Vanguard FTSE Canada All Cap Index ETF',
        'VGRO.TO': 'Vanguard Growth ETF Portfolio'
    },
    'UK': {
        'VUSA.L': 'Vanguard S&P 500 UCITS ETF',
        'VWRL.L': 'Vanguard FTSE All-World UCITS ETF',
        'VUKE.L': 'Vanguard FTSE 100 UCITS ETF'
    },
    'GERMANY': {
        'IWDA.DE': 'iShares Core MSCI World UCITS ETF',
        'VWCE.DE': 'Vanguard FTSE All-World UCITS ETF'
    },
    'INTERNATIONAL': {
        'EFA': 'iShares MSCI EAFE ETF',
        'VEA': 'Vanguard FTSE Developed Markets ETF',
        'EEM': 'iShares MSCI Emerging Markets ETF',
        'VWO': 'Vanguard FTSE Emerging Markets ETF'
    }
}

# Flatten ETF list
ALL_ETFS = {}
for country, etfs in GLOBAL_ETF_DATABASE.items():
    ALL_ETFS.update(etfs)

country_display_names = {
    'USA': '🇺🇸 United States',
    'CANADA': '🇨🇦 Canada', 
    'UK': '🇬🇧 United Kingdom',
    'GERMANY': '🇩🇪 Germany',
    'INTERNATIONAL': '🌐 International'
}

# Sidebar
st.sidebar.title("🌍 Global ETF Navigator")
page = st.sidebar.selectbox("Choose a section:", 
                           ["🏆 Top Global Performers", 
                            "🔍 Search ETFs by Country", 
                            "💰 Investment Calculator", 
                            "⚖️ Compare ETFs"])

st.sidebar.markdown("---")
st.sidebar.subheader("Filter by Country/Region")
selected_country = st.sidebar.selectbox(
    "Select Country/Region:",
    ["All Countries"] + list(GLOBAL_ETF_DATABASE.keys()),
    format_func=lambda x: country_display_names.get(x, x) if x != "All Countries" else "🌍 All Countries"
)

# Helper Functions
def get_etf_data(symbol):
    """Get ETF data safely"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max")
        info = ticker.info
        
        if hist.empty or len(hist) < 10:
            return None
            
        first_price = hist['Close'].iloc[0]
        last_price = hist['Close'].iloc[-1]
        years = (hist.index[-1] - hist.index[0]).days / 365.25
        
        if years <= 0:
            return None
            
        cagr = ((last_price / first_price) ** (1/years) - 1) * 100
        expense_ratio = info.get('annualReportExpenseRatio', 0.005) * 100
        
        return {
            'symbol': symbol,
            'name': ALL_ETFS.get(symbol, info.get('longName', 'Unknown')),
            'cagr': round(cagr, 2),
            'expense_ratio': round(expense_ratio, 3),
            'years': round(years, 1),
            'current_price': round(last_price, 2),
            'first_price': first_price,
            'last_price': last_price,
            'hist': hist
        }
    except Exception as e:
        return None

def calculate_investment_growth(symbol, amount):
    """Calculate investment growth with expense ratio"""
    try:
        data = get_etf_data(symbol)
        if not data:
            return None
            
        # Gross returns (before fees)
        gross_value = amount * (data['last_price'] / data['first_price'])
        gross_return = ((gross_value / amount) - 1) * 100
        
        # Net returns (after fees)
        expense_ratio = data['expense_ratio'] / 100
        fee_multiplier = (1 - expense_ratio) ** data['years']
        net_value = gross_value * fee_multiplier
        net_return = ((net_value / amount) - 1) * 100
        
        total_fees = gross_value - net_value
        
        return {
            'symbol': symbol,
            'initial_investment': amount,
            'gross_value': gross_value,
            'net_value': net_value,
            'gross_return': gross_return,
            'net_return': net_return,
            'total_fees': total_fees,
            'expense_ratio': data['expense_ratio'],
            'years': data['years'],
            'cagr': data['cagr']
        }
    except Exception as e:
        return None

# Main Content
if page == "🏆 Top Global Performers":
    st.header("🏆 Top Performing ETFs Worldwide")
    
    if selected_country != "All Countries":
        st.markdown(f"**Best Performing ETFs from {country_display_names.get(selected_country)}**")
        etf_dict = GLOBAL_ETF_DATABASE.get(selected_country, {})
    else:
        st.markdown("**Best Performing ETFs from Around the World**")
        etf_dict = ALL_ETFS
    
    st.markdown("Find the highest returning ETFs with real-time CAGR calculations, expense ratios, and performance metrics.")
    
    # Add explanatory text for beginners
    with st.expander("📚 What are ETFs and why should I care?"):
        st.markdown("""
        **ETF (Exchange-Traded Fund)** is like a basket of stocks or bonds that you can buy with one purchase. 
        Think of it as buying a slice of many companies at once, which helps spread your risk.
        
        **Key Terms:**
        - **CAGR**: Compound Annual Growth Rate - the average yearly return of your investment
        - **Expense Ratio**: The annual fee charged by the ETF (lower is better)
        - **Years**: How long the ETF has been trading
        """)
    
    # Loading data
    with st.spinner("Loading ETF data... This may take a moment."):
        results = []
        symbols_to_check = list(etf_dict.items())[:8]  # Limit for demo
        
        progress_bar = st.progress(0)
        for i, (symbol, name) in enumerate(symbols_to_check):
            progress_bar.progress((i + 1) / len(symbols_to_check))
            data = get_etf_data(symbol)
            if data:
                results.append({
                    'Symbol': data['symbol'],
                    'Name': data['name'],
                    'CAGR (%)': data['cagr'],
                    'Expense Ratio (%)': data['expense_ratio'],
                    'Years': data['years']
                })
        
        progress_bar.empty()
        
        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('CAGR (%)', ascending=False)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_cagr = df['CAGR (%)'].mean()
                st.metric("Average CAGR", f"{avg_cagr:.2f}%")
            with col2:
                best_performer = df.iloc[0]
                st.metric("Best Performer", f"{best_performer['Symbol']}", f"{best_performer['CAGR (%)']:.2f}%")
            with col3:
                avg_expense = df['Expense Ratio (%)'].mean()
                st.metric("Avg Expense Ratio", f"{avg_expense:.3f}%")
            
            # Display table
            st.subheader("📋 Detailed ETF Information")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Create visualization
            st.subheader("📈 CAGR Comparison Chart")
            fig = px.bar(df, x='Symbol', y='CAGR (%)', 
                        title="CAGR Since Inception by ETF",
                        color='CAGR (%)', color_continuous_scale='RdYlGn')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Unable to load ETF data. Please try again later.")

elif page == "🔍 Search ETFs by Country":
    st.header("🔍 ETF Search & Analysis")
    
    # Search section
    search_term = st.text_input("🔍 Search for ETF (by symbol or name):", placeholder="Type ETF symbol or name...")
    
    if search_term:
        search_results = []
        search_term = search_term.upper()
        
        for symbol, name in ALL_ETFS.items():
            if search_term in symbol.upper() or search_term in name.upper():
                # Find country
                etf_country = "Unknown"
                for country, etfs in GLOBAL_ETF_DATABASE.items():
                    if symbol in etfs:
                        etf_country = country
                        break
                
                search_results.append({
                    'symbol': symbol, 
                    'name': name,
                    'country': etf_country
                })
        
        if search_results:
            st.subheader(f"📋 Search Results for '{search_term}'")
            for i, result in enumerate(search_results[:10]):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"Analyze {result['symbol']}", key=f"analyze_{i}"):
                        st.session_state.selected_etf = result['symbol']
                with col2:
                    st.write(f"**{result['symbol']}** - {result['name']} ({country_display_names.get(result['country'], result['country'])})")
        else:
            st.warning(f"No ETFs found matching '{search_term}'")
    
    # ETF Analysis
    if 'selected_etf' in st.session_state or not search_term:
        st.subheader("📊 ETF Analysis")
        
        if 'selected_etf' in st.session_state:
            default_symbol = st.session_state.selected_etf
        else:
            default_symbol = 'SPY'
        
        etf_symbols = sorted(list(ALL_ETFS.keys()))
        selected_symbol = st.selectbox(
            "Select ETF for detailed analysis:",
            etf_symbols,
            index=etf_symbols.index(default_symbol) if default_symbol in etf_symbols else 0,
            format_func=lambda x: f"{x} - {ALL_ETFS[x]}"
        )
        
        if st.button("🔍 Analyze ETF"):
            with st.spinner(f"Analyzing {selected_symbol}..."):
                data = get_etf_data(selected_symbol)
                
                if data:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current Price", f"${data['current_price']}")
                    with col2:
                        st.metric("CAGR Since Inception", f"{data['cagr']:.2f}%")
                    with col3:
                        st.metric("Expense Ratio", f"{data['expense_ratio']:.3f}%")
                    with col4:
                        st.metric("Years Since Inception", f"{data['years']:.1f}")
                    
                    # Quick investment scenarios
                    st.subheader("💰 Quick Investment Scenarios")
                    scenario_cols = st.columns(3)
                    
                    for i, amount in enumerate([1000, 5000, 10000]):
                        result = calculate_investment_growth(selected_symbol, amount)
                        if result:
                            with scenario_cols[i]:
                                gain = result['net_value'] - amount
                                gain_pct = result['net_return']
                                st.metric(
                                    f"${amount:,} Investment",
                                    f"${result['net_value']:,.0f}",
                                    f"+${gain:,.0f} ({gain_pct:.1f}%)"
                                )
                else:
                    st.error(f"Unable to analyze {selected_symbol}")

elif page == "💰 Investment Calculator":
    st.header("💰 Investment Growth Calculator")
    
    with st.expander("🎯 How to use this calculator"):
        st.markdown("""
        This calculator shows you how your investment would have grown if you had invested 
        a specific amount in an ETF since its inception date, including the impact of fees.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Select ETF")
        etf_symbols = sorted(list(ALL_ETFS.keys()))
        selected_etf = st.selectbox(
            "Choose an ETF:", 
            etf_symbols,
            format_func=lambda x: f"{x} - {ALL_ETFS[x]}"
        )
        
        investment_amount = st.number_input(
            "Investment Amount ($)", 
            min_value=100, 
            max_value=1000000, 
            value=1000, 
            step=100
        )
    
    with col2:
        st.subheader("Calculation Results")
        
        with st.spinner(f"Calculating returns for {selected_etf}..."):
            result = calculate_investment_growth(selected_etf, investment_amount)
            
            if result:
                st.success(f"✅ Data loaded for {selected_etf}")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.metric("Initial Investment", f"${investment_amount:,}")
                    st.metric("Gross Value (Before Fees)", f"${result['gross_value']:,.2f}", 
                             f"{result['gross_return']:.1f}%")
                
                with col_b:
                    st.metric("Net Value (After Fees)", f"${result['net_value']:,.2f}", 
                             f"{result['net_return']:.1f}%")
                    st.metric("Total Fees Paid", f"${result['total_fees']:,.2f}")
                
                st.info(f"**Expense Ratio:** {result['expense_ratio']:.3f}% annually | **Years Invested:** {result['years']:.1f}")
                
                if result['total_fees'] > 0:
                    fee_impact = (result['total_fees'] / result['gross_value']) * 100
                    st.warning(f"💡 **Fee Impact:** The expense ratio reduced your returns by ${result['total_fees']:,.2f} ({fee_impact:.1f}% of gross value)")
            else:
                st.error(f"Unable to fetch data for {selected_etf}")

elif page == "⚖️ Compare ETFs":
    st.header("⚖️ ETF Comparison Tool")
    
    with st.expander("📖 How to compare ETFs"):
        st.markdown("""
        When comparing ETFs, consider these factors:
        1. **CAGR**: Higher is generally better, but consider the risk
        2. **Expense Ratio**: Lower fees mean more money stays in your pocket
        3. **Years**: How long the ETF has been trading
        """)
    
    col1, col2 = st.columns(2)
    etf_options = sorted(list(ALL_ETFS.keys()))
    
    with col1:
        etf1 = st.selectbox(
            "Select first ETF:", 
            etf_options, 
            index=0,
            format_func=lambda x: f"{x} - {ALL_ETFS[x]}"
        )
    
    with col2:
        etf2 = st.selectbox(
            "Select second ETF:", 
            etf_options, 
            index=1 if len(etf_options) > 1 else 0,
            format_func=lambda x: f"{x} - {ALL_ETFS[x]}"
        )
    
    if st.button("Compare ETFs"):
        with st.spinner("Comparing ETFs..."):
            result1 = calculate_investment_growth(etf1, 1000)
            result2 = calculate_investment_growth(etf2, 1000)
            
            if result1 and result2:
                st.subheader(f"📊 {etf1} vs {etf2} Comparison ($1,000 Investment)")
                
                comp_data = {
                    'Metric': [
                        'Net Value (After Fees)', 
                        'Gross Value (Before Fees)',
                        'Net Return (%)', 
                        'Gross Return (%)',
                        'Total Fees Paid',
                        'Expense Ratio (%)',
                        'Years'
                    ],
                    etf1: [
                        f"${result1['net_value']:,.2f}",
                        f"${result1['gross_value']:,.2f}",
                        f"{result1['net_return']:.1f}%",
                        f"{result1['gross_return']:.1f}%",
                        f"${result1['total_fees']:,.2f}",
                        f"{result1['expense_ratio']:.3f}%",
                        f"{result1['years']:.1f}"
                    ],
                    etf2: [
                        f"${result2['net_value']:,.2f}",
                        f"${result2['gross_value']:,.2f}",
                        f"{result2['net_return']:.1f}%",
                        f"{result2['gross_return']:.1f}%",
                        f"${result2['total_fees']:,.2f}",
                        f"{result2['expense_ratio']:.3f}%",
                        f"{result2['years']:.1f}"
                    ]
                }
                
                comp_df = pd.DataFrame(comp_data)
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
                
                # Determine winner
                if result1['net_value'] > result2['net_value']:
                    winner = etf1
                    winner_value = result1['net_value']
                    loser_value = result2['net_value']
                else:
                    winner = etf2
                    winner_value = result2['net_value']
                    loser_value = result1['net_value']
                
                difference = winner_value - loser_value
                st.success(f"🏆 **{winner}** performed better with a net value of **${winner_value:,.2f}** (${difference:,.2f} more)")
                
                # Fee impact analysis
                if result1['total_fees'] != result2['total_fees']:
                    if result1['total_fees'] > result2['total_fees']:
                        st.info(f"💡 **Fee Analysis:** {etf1} charged ${result1['total_fees'] - result2['total_fees']:.2f} more in fees than {etf2}")
                    else:
                        st.info(f"💡 **Fee Analysis:** {etf2} charged ${result2['total_fees'] - result1['total_fees']:.2f} more in fees than {etf1}")
            else:
                st.error("Unable to compare ETFs. Please try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<small>
📈 Global ETF Performance Analyzer | Built for Investment Beginners<br>
<strong>Disclaimer:</strong> This tool is for educational purposes only. Past performance does not guarantee future results. 
Always consult with a financial advisor before making investment decisions.
</small>
</div>
""", unsafe_allow_html=True)