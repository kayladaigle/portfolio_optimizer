import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from optimization import stock_optimization

# read csv of forecasted returns
returns_data = pd.read_csv('forecasted_returns.csv')

# columns renamed
returns_data.columns = ['stock_symbol', 'index', 'date', 'yhat']

# correct data for optimization - datatime format
returns_data['date'] = pd.to_datetime(returns_data['date'])
returns_data.set_index('date', inplace=True)

# ensure yhat is numeric
returns_data['yhat'] = pd.to_numeric(returns_data['yhat'])

# risk categories for user
risk_choices = {
    'low': 0.05,
    'medium': 0.10,
    'high': 0.20,
}

with st.sidebar:
    st.header('Select Your Preferences')

    # Risk preference slider
    user_risk_choice = st.select_slider('Risk Level', ['low', 'medium', 'high'])
    choice = risk_choices[user_risk_choice]

    # give option of all stocks
    all_stocks = returns_data['stock_symbol'].unique()

    selected_assets = st.multiselect('Preferred Assets for Portfolio Optimization', all_stocks, default=['AMZN', 'GOOGL'])
    st.selectbox("Would you like to diversify your portfolio?",['No, use only selected assets', 'Yes, let the optimizer add more assets'])

    forecast_period = st.slider('Forecast Period (in days)', 1, 365, 30)
    st.divider()
    st.sidebar.info("""
    ## FAQ:
    ## What is Low, Medium, or High Risk in a Stock Portfolio?
    * Low Risk: (5%) Stable, big companies. Lower returns, less volatility.
    * Medium Risk: (10%) Growing companies. Balanced returns and risk.
    * High Risk: (20%) Small or new companies. High risk, high potential return.

    ## What Are Assets in a Stock Portfolio?
    Assets are the stocks or funds in your portfolio. Each has different risk and return.

    ## How Many Assets Should I Choose? (Why is Stock Diversity Important?)
    Having 10-20 stocks across different sectors reduces risk. More diversity = less chance of big losses.
    
    ## What Does "Forecasted Period" Mean?
    The forecasted period is how long you plan to hold your investments. Longer = more risk you can take.

    """)

st.title('Stock Portfolio Optimizer')
#  selected inputs
st.write(f"Risk Level: {choice * 100}%")
st.write(f"Preferred Assets: {selected_assets}")
st.write(f"Forecasted Time Period: {forecast_period} days")


selected_data = returns_data[returns_data['stock_symbol'].isin(selected_assets)]

optimal_weights, portfolio_return, portfolio_risk = stock_optimization(selected_data,choice)

st.write("Optimal Portfolio Weights:")
weights_df = pd.DataFrame(optimal_weights, columns=["Optimal Weight"], index=selected_assets)
st.dataframe(weights_df)

st.write(f"Expected Portfolio Return: {portfolio_return * 100:.2f}%")
st.write(f"Portfolio Risk (Standard Deviation): {portfolio_risk * 100:.2f}%")
st.divider()

col1, col2 = st.columns(2)
# column 1
with col1:

    fig = go.Figure(data=[go.Pie(labels=selected_assets, values=optimal_weights)])
    fig.update_layout(title="Portfolio Allocation")
    st.plotly_chart(fig)

    # Cumulative Returns Chart (simulate for demonstration)
    dates = pd.date_range(start="2024-01-01", periods=forecast_period, freq='D')
    cumulative_returns = np.cumsum(np.random.randn(forecast_period) * portfolio_return)  # Simulate returns

#column 2
with col2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dates, y=cumulative_returns, mode='lines', name='Cumulative Return'))
    fig2.update_layout(title="Portfolio Performance Forecasted Period",
                   xaxis_title="Date",
                   yaxis_title="Cumulative Return")
    st.plotly_chart(fig2)

