import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from optimization import stock_optimization
from data_processing import returns

# HISTORICAL DATA PREPARATION FOR OPTIMIZATION *****************************

returns_formatted = returns.melt(id_vars=['Date'],
                           var_name = 'Stock',
                           value_name = 'Return')

returns_formatted.rename(columns= {'Date':'ds','Return':'y'},inplace=True)

historical_data = {stock:group[['ds','y']] for stock, group in returns_formatted.groupby('Stock')}

# turn returns dictionary into dataframe
historical_data_df = pd.concat(historical_data.values(), ignore_index=True)

#historical_data_df.columns = ['stock_symbol', 'index', 'date', 'yhat']

# correct data for optimization - datatime format
historical_data_df['ds'] = pd.to_datetime(historical_data_df['ds'])
historical_data_df.set_index('ds', inplace=True)

# ensure yhat is numeric
historical_data_df['y'] = pd.to_numeric(historical_data_df['y'])



# **********************************



# risk categories for user
risk_choices = {
    'low': 0.05,
    'medium': 0.10,
    'high': 0.20,
}

# SIDEBAR *******************************************
with st.sidebar:
    st.header('Select Your Preferences')

    # Risk preference slider
    user_risk_choice = st.select_slider('Risk Level', ['low', 'medium', 'high'])
    choice = risk_choices[user_risk_choice]

    # give option of all stocks
    all_stocks = returns_formatted['Stock'].unique()

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

    #********************************************

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

def diversify_portfolio(returns, selected_assets, diversify):
    if diversify == 'No, use only selected assets':
        selected_data = returns[returns['Stock'].isin(selected_assets)]
        final_assets = selected_assets
        return final_assets, selected_data
    else:
        all_stocks = returns.pivot_table(index='ds',columns='Stock', values='y')
        correlation = all_stocks.corr()
        selected_correlation = correlation[selected_assets].mean(axis=1)
        not_selected = [asset for asset in all_stocks.columns if asset not in selected_assets]
        sorted_correlation = selected_correlation.loc[not_selected].sort_values(ascending=True)
        selected_for_diversity = sorted_correlation.head(7).index.tolist()
        final_assets = selected_for_diversity + selected_assets
        selected_data = returns[returns['Stock'].isin(final_assets)]
        return final_assets , selected_data

final_assets, selected_data = diversify_portfolio(returns_formatted, selected_assets, diversify_option)

# TEST FOR OPTIMIZATION ******************************
# creating asset allocation where weights are equal to compare against optimal weight

#def equal_weights(assets):
    #num_assets = len(assets)
    #equal_weights = np.ones(num_assets) / num_assets
    #return equal_weights

#equal_weights = equal_weights(final_assets)

#print("Equal Weights:", equal_weights)
#st.write("Equal Portfolio Weights:")
#equal_weights_df = pd.DataFrame(equal_weights, columns=["equal_weights"], index=final_assets)
#st.dataframe(equal_weights_df)

#equal_pivot = selected_data.pivot_table(index='ds', columns='Stock', values='y')
#equal_cov_matrix = equal_pivot.cov().values

#equal_mean_returns = selected_data.groupby('Stock')['y'].mean()
#equal_portfolio_return = np.dot(equal_weights, equal_mean_returns)
#equal_portfolio_risk = np.sqrt(np.dot(equal_weights.T, np.dot(equal_cov_matrix, equal_weights)))

#st.write(f"Expected Portfolio Return: {equal_portfolio_return * 100:.2f}%")
#st.write(f"Equal Portfolio Risk (Standard Deviation): {equal_portfolio_risk * 100:.2f}%")


# *************************************************



# send for optimization

# optimal weight data
optimal_weights, portfolio_return, portfolio_risk = stock_optimization(selected_data,user_risk_choice)

print("Optimal Weights:", optimal_weights)
st.write("Optimal Portfolio Weights:")
weights_df = pd.DataFrame(optimal_weights, columns=["Optimal Weight"], index=final_assets)
st.dataframe(weights_df)

# expected return and portfolio risk

st.write(f"Expected Portfolio Return: {portfolio_return * 100:.2f}%")
st.write(f"Portfolio Risk (Standard Deviation): {portfolio_risk * 100:.2f}%")
st.divider()



# VISUALIZATIONS ******************************

col1, col2 = st.columns(2)
# column 1
# optimal weight chart
with col1:

    fig = go.Figure(data=[go.Pie(labels=final_assets, values=optimal_weights)])
    fig.update_layout(title="Portfolio Allocation")
    st.plotly_chart(fig)

# column 2
# performance over time graph

# read csv of forecasted returns
returns_data = pd.read_csv('forecasted_five_year_returns.csv')

# columns renamed
returns_data.columns = ['stock_symbol', 'index', 'date', 'yhat']

# correct data for optimization - datatime format
returns_data['date'] = pd.to_datetime(returns_data['date'])
returns_data.set_index('date', inplace=True)

# ensure yhat is numeric
returns_data['yhat'] = pd.to_numeric(returns_data['yhat'])


with col2:

    # Filter the returns_data for the selected stocks
    selected_data_for_forecast = returns_data[returns_data['stock_symbol'].isin(selected_assets)]

    # Resample the data to daily forecasted returns for the selected stocks
    # We will calculate the average 'yhat' for the selected stocks on each day
    daily_forecasted_returns = selected_data_for_forecast.groupby('date')['yhat'].mean()

    # Cumulative Returns Chart (simulate for demonstration)
    dates = pd.date_range(start="2024-01-01", periods=forecast_period, freq='D')
    cumulative_returns = (1 + daily_forecasted_returns).cumprod() - 1

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=dates, y=cumulative_returns, mode='lines', name='Cumulative Return'))
    fig2.update_layout(title="Portfolio Performance Forecasted Period",
                   xaxis_title="Date",
                   yaxis_title="Cumulative Return")
    st.plotly_chart(fig2)







