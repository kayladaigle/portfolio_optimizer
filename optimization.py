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

    if risk_tolerance == 'low':
        risk_scale = 0.20
    elif risk_tolerance == 'medium':
        risk_scale = 0.50
    elif risk_tolerance == 'high':
        risk_scale = 0.80
    else:
        risk_scale = 0.50

    risk_cov_matrix = risk_scale * cov_matrix

    # number of assets
    n = len(mean_returns)

    # building quadratic programming problem

    P = cvx.matrix(risk_cov_matrix)
    q = cvx.matrix(np.zeros((n,1)))

    A = cvx.matrix(np.ones((1,n)))
    b = cvx.matrix(1.0)

    G = cvx.matrix(np.diag(-np.ones(n)))
    h = cvx.matrix(np.zeros(n))

    # solve problem
    sol = solvers.qp(P, q, G, h, A, b)

    optimal_weights = np.array(sol['x']).flatten()

    portfolio_return = np.dot(optimal_weights, mean_returns)
    portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(risk_cov_matrix, optimal_weights)))

    return optimal_weights, portfolio_return, portfolio_risk
