# use forecasted return data created with Prophet to optimize with CvXopt

import numpy as np
import pandas as pd
import cvxopt as cvx
from cvxopt import blas, solvers
import streamlit as st


def stock_optimization(returns_data, risk_tolerance):

    # group by stock symbols
    mean_returns = returns_data.groupby('stock_symbol')['yhat'].mean()

    # reshape data so that each stock symbol is a column - calculate covariance between stocks
    pivot = returns_data.pivot_table(index='date', columns='stock_symbol', values='yhat')
    cov_matrix = pivot.cov().values

    # number of assets
    n = len(mean_returns)

    # building quadratic programming problem

    P = cvx.matrix(cov_matrix)
    q = cvx.matrix(np.zeros((n,1)))

    A = cvx.matrix(np.ones((1,n)))
    b = cvx.matrix(1.0)

    G = cvx.matrix(np.diag(-np.ones(n)))
    h = cvx.matrix(np.zeros(n))

    # solve problem
    sol = solvers.qp(P, q, G, h, A, b)

    optimal_weights = np.array(sol['x']).flatten()

    portfolio_return = np.dot(optimal_weights, mean_returns)
    portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))

    return optimal_weights, portfolio_return, portfolio_risk
