import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
from etf_data import ETFAnalyzer
from calculators import InvestmentCalculator

# Page configuration
st.set_page_config(
    page_title="ETF Performance Analyzer",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'etf_data' not in st.session_state:
    st.session_state.etf_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Main title
st.title("📈 ETF Performance Analyzer")
st.markdown("**Discover top-performing ETFs and calculate your potential investment returns**")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a section:", 
                           ["Top Performers", "Investment Calculator", "ETF Comparison"])

# Initialize analyzers
etf_analyzer = ETFAnalyzer()
calculator = InvestmentCalculator()

# Cache data for 1 hour to avoid repeated API calls
@st.cache_data(ttl=3600)
def load_etf_data():
    return etf_analyzer.get_top_etfs()

# Main content based on selected page
if page == "Top Performers":
    st.header("🏆 Top Performing ETFs")
    
    # Add explanatory text for beginners
    with st.expander("📚 What are ETFs and why should I care?"):
        st.markdown("""
        **ETF (Exchange-Traded Fund)** is like a basket of stocks or bonds that you can buy with one purchase. 
        Think of it as buying a slice of many companies at once, which helps spread your risk.
        
        **Key Terms:**
        - **CAGR**: Compound Annual Growth Rate - the average yearly return of your investment
        - **Expense Ratio**: The annual fee charged by the ETF (lower is better)
        - **AUM**: Assets Under Management - total money invested in the ETF
        - **Inception Date**: When the ETF first started trading
        """)
    
    # Loading data
    with st.spinner("Loading ETF data... This may take a moment."):
        try:
            etf_data = load_etf_data()
            
            if etf_data is not None and not etf_data.empty:
                # Display top performers
                st.subheader("📊 Performance Overview")
                
                # Create columns for metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_cagr = etf_data['CAGR (%)'].mean()
                    st.metric("Average CAGR", f"{avg_cagr:.2f}%")
                
                with col2:
                    best_performer = etf_data.loc[etf_data['CAGR (%)'].idxmax()]
                    st.metric("Best Performer", f"{best_performer['Symbol']}", 
                             f"{best_performer['CAGR (%)']:.2f}%")
                
                with col3:
                    avg_expense = etf_data['Expense Ratio (%)'].mean()
                    st.metric("Avg Expense Ratio", f"{avg_expense:.3f}%")
                
                # Display the data table
                st.subheader("📋 Detailed ETF Information")
                
                # Format the dataframe for better display
                display_df = etf_data.copy()
                display_df['CAGR (%)'] = display_df['CAGR (%)'].apply(lambda x: f"{x:.2f}%")
                display_df['Expense Ratio (%)'] = display_df['Expense Ratio (%)'].apply(lambda x: f"{x:.3f}%")
                display_df['AUM (Billions)'] = display_df['AUM (Billions)'].apply(lambda x: f"${x:.1f}B")
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Create visualization
                st.subheader("📈 CAGR Comparison Chart")
                fig = px.bar(
                    etf_data, 
                    x='Symbol', 
                    y='CAGR (%)',
                    title="CAGR Since Inception by ETF",
                    color='CAGR (%)',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error("Unable to load ETF data. Please try again later.")
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            st.info("This might be due to API rate limits. Please try again in a few minutes.")

elif page == "Investment Calculator":
    st.header("💰 Investment Growth Calculator")
    
    # Explanatory section
    with st.expander("🎯 How to use this calculator"):
        st.markdown("""
        This calculator shows you how your investment would have grown if you had invested 
        a specific amount in an ETF since its inception date.
        
        **Example**: If you invested $1,000 in an ETF with 10% CAGR for 5 years, 
        your investment would be worth approximately $1,610 today.
        """)
    
    # Input section
    col1, col2 = st.columns(2)
    
    with col1:
        # ETF selection
        st.subheader("Select ETF")
        etf_symbols = ['SPY', 'QQQ', 'VTI', 'IWM', 'EFA', 'EEM', 'VNQ', 'GLD', 'TLT', 'HYG']
        selected_etf = st.selectbox("Choose an ETF:", etf_symbols)
        
        # Investment amount
        investment_amount = st.number_input(
            "Investment Amount ($)", 
            min_value=100, 
            max_value=1000000, 
            value=1000, 
            step=100
        )
    
    with col2:
        st.subheader("Calculation Results")
        
        # Fetch ETF data and calculate returns
        with st.spinner(f"Calculating returns for {selected_etf}..."):
            try:
                result = calculator.calculate_investment_growth(selected_etf, investment_amount)
                
                if result:
                    # Display results
                    st.success(f"✅ Data loaded for {selected_etf}")
                    
                    # Key metrics
                    st.metric("Initial Investment", f"${investment_amount:,}")
                    st.metric("Current Value", f"${result['current_value']:,.2f}", 
                             f"{result['total_return']:.1f}%")
                    st.metric("CAGR", f"{result['cagr']:.2f}%")
                    st.metric("Years Invested", f"{result['years']:.1f}")
                    
                    # Show growth chart
                    if 'growth_data' in result:
                        st.subheader("📈 Investment Growth Over Time")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=result['growth_data']['Date'],
                            y=result['growth_data']['Portfolio_Value'],
                            mode='lines',
                            name='Portfolio Value',
                            line=dict(color='green', width=2)
                        ))
                        fig.update_layout(
                            title=f"Growth of ${investment_amount:,} Investment in {selected_etf}",
                            xaxis_title="Date",
                            yaxis_title="Portfolio Value ($)",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.error(f"Unable to fetch data for {selected_etf}")
                    
            except Exception as e:
                st.error(f"Error calculating returns: {str(e)}")
    
    # Comparison section
    st.subheader("🔍 Compare Multiple Scenarios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        amount_1000 = calculator.quick_calculation(selected_etf, 1000)
        if amount_1000:
            st.info(f"**$1,000** → **${amount_1000['current_value']:,.0f}**")
    
    with col2:
        amount_5000 = calculator.quick_calculation(selected_etf, 5000)
        if amount_5000:
            st.info(f"**$5,000** → **${amount_5000['current_value']:,.0f}**")
    
    with col3:
        amount_10000 = calculator.quick_calculation(selected_etf, 10000)
        if amount_10000:
            st.info(f"**$10,000** → **${amount_10000['current_value']:,.0f}**")

elif page == "ETF Comparison":
    st.header("⚖️ ETF Comparison Tool")
    
    with st.expander("📖 How to compare ETFs"):
        st.markdown("""
        When comparing ETFs, consider these factors:
        1. **CAGR**: Higher is generally better, but consider the risk
        2. **Expense Ratio**: Lower fees mean more money stays in your pocket
        3. **AUM**: Larger funds are typically more stable
        4. **Volatility**: How much the price swings up and down
        """)
    
    # ETF selection for comparison
    col1, col2 = st.columns(2)
    
    etf_options = ['SPY', 'QQQ', 'VTI', 'IWM', 'EFA', 'EEM', 'VNQ', 'GLD', 'TLT', 'HYG']
    
    with col1:
        etf1 = st.selectbox("Select first ETF:", etf_options, index=0)
    
    with col2:
        etf2 = st.selectbox("Select second ETF:", etf_options, index=1)
    
    if st.button("Compare ETFs"):
        with st.spinner("Comparing ETFs..."):
            try:
                comparison = calculator.compare_etfs(etf1, etf2, 1000)
                
                if comparison:
                    st.subheader(f"📊 {etf1} vs {etf2} Comparison")
                    
                    # Create comparison table
                    comp_data = {
                        'Metric': ['Current Value', 'Total Return (%)', 'CAGR (%)', 'Years'],
                        etf1: [
                            f"${comparison[etf1]['current_value']:,.2f}",
                            f"{comparison[etf1]['total_return']:.1f}%",
                            f"{comparison[etf1]['cagr']:.2f}%",
                            f"{comparison[etf1]['years']:.1f}"
                        ],
                        etf2: [
                            f"${comparison[etf2]['current_value']:,.2f}",
                            f"{comparison[etf2]['total_return']:.1f}%",
                            f"{comparison[etf2]['cagr']:.2f}%",
                            f"{comparison[etf2]['years']:.1f}"
                        ]
                    }
                    
                    comp_df = pd.DataFrame(comp_data)
                    st.dataframe(comp_df, use_container_width=True, hide_index=True)
                    
                    # Determine winner
                    if comparison[etf1]['current_value'] > comparison[etf2]['current_value']:
                        winner = etf1
                        winner_value = comparison[etf1]['current_value']
                    else:
                        winner = etf2
                        winner_value = comparison[etf2]['current_value']
                    
                    st.success(f"🏆 **{winner}** performed better with a final value of **${winner_value:,.2f}**")
                
                else:
                    st.error("Unable to compare ETFs. Please try again.")
                    
            except Exception as e:
                st.error(f"Error comparing ETFs: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
<small>
📈 ETF Performance Analyzer | Built for Investment Beginners<br>
<strong>Disclaimer:</strong> This tool is for educational purposes only. Past performance does not guarantee future results. 
Always consult with a financial advisor before making investment decisions.
</small>
</div>
""", unsafe_allow_html=True)
