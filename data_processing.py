import pandas as pd

# Load CSV files into dataframe

bonds = pd.read_csv('data/stock_csvs/bond_etfs.csv')
mag7 = pd.read_csv('data/stock_csvs/mag7.csv')
metals = pd.read_csv('data/stock_csvs/metals_etfs.csv')
equity = pd.read_csv('data/stock_csvs/equity_etfs.csv')

# double check to ensure all files are on same time window

bonds['Date'] = pd.to_datetime(bonds['Date'])
mag7['Date'] = pd.to_datetime(mag7['Date'])
metals['Date'] = pd.to_datetime(metals['Date'])
equity['Date'] = pd.to_datetime(equity['Date'])

# merge dataframes on date column to combine dataframes

all_stocks = pd.merge(bonds, mag7, on='Date', how='outer')
all_stocks = pd.merge(all_stocks, metals, on='Date', how='outer')
all_stocks = pd.merge(all_stocks, equity, how='outer')

# handle missing values by filling forward to avoid errors

all_stocks.ffill(inplace=True)

# change prices to returns in dataframe

returns = all_stocks.set_index('Date').pct_change()

returns.reset_index(inplace=True)

# print(returns)
# print(returns.dtypes)