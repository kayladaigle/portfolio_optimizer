import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from optimization import stock_optimization

# read csv of forecasted returns
returns_data = pd.read_csv('forecasted_five_year_returns.csv')

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
    diversify_option = st.selectbox("Would you like to diversify your portfolio?",['No, use only selected assets', 'Yes, let the optimizer add more assets'])

    # Slider to select the forecast period in years (1 to 5 years)
    forecast_years = st.slider('Select Forecast Period (in Years)', min_value=1, max_value=5, value=1)

    forecast_period = forecast_years * 365

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

# top of page

st.title('Stock Portfolio Optimizer')

#  selected inputs
st.write(f"Risk Level: {user_risk_choice}")
st.write(f"Preferred Assets: {selected_assets}")

if forecast_years == 1:
    st.write(f"Forecasted Time Period: {forecast_years} year")
else:
    st.write(f"Forecasted Time Period: {forecast_years} years")


# diversify function

def diversify_portfolio(returns_data, selected_assets, diversify):
    if diversify == 'No, use only selected assets':
        selected_data = returns_data[returns_data['stock_symbol'].isin(selected_assets)]
        final_assets = selected_assets
        return final_assets, selected_data
    else:
        all_stocks = returns_data.pivot_table(index='date',columns='stock_symbol', values='yhat')
        correlation = all_stocks.corr()
        selected_correlation = correlation[selected_assets].mean(axis=1)
        not_selected = [asset for asset in all_stocks.columns if asset not in selected_assets]
        sorted_correlation = selected_correlation.loc[not_selected].sort_values(ascending=True)
        selected_for_diversity = sorted_correlation.head(7).index.tolist()
        final_assets = selected_for_diversity + selected_assets
        selected_data = returns_data[returns_data['stock_symbol'].isin(final_assets)]
        return final_assets , selected_data


final_assets, selected_data = diversify_portfolio(returns_data, selected_assets, diversify_option)
# optimal weight data
optimal_weights, portfolio_return, portfolio_risk = stock_optimization(selected_data,user_risk_choice)

st.write("Optimal Portfolio Weights:")
weights_df = pd.DataFrame(optimal_weights, columns=["Optimal Weight"], index=final_assets)
st.dataframe(weights_df)

# expected return and portfolio risk

st.write(f"Expected Portfolio Return: {portfolio_return * 100:.2f}%")
st.write(f"Portfolio Risk (Standard Deviation): {portfolio_risk * 100:.2f}%")
st.divider()

col1, col2 = st.columns(2)
# column 1
# optimal weight chart
with col1:

    fig = go.Figure(data=[go.Pie(labels=final_assets, values=optimal_weights)])
    fig.update_layout(title="Portfolio Allocation")
    st.plotly_chart(fig)

#column 2
# performance over time graph
with col2:

    # Cumulative Returns Chart (simulate for demonstration)
    dates = pd.date_range(start="2024-01-01", periods=forecast_period, freq='D')
    cumulative_returns = np.cumsum(np.random.randn(forecast_period) * portfolio_return)  # Simulate returns

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dates, y=cumulative_returns, mode='lines', name='Cumulative Return'))
    fig2.update_layout(title="Portfolio Performance Forecasted Period",
                   xaxis_title="Date",
                   yaxis_title="Cumulative Return")
    st.plotly_chart(fig2)


