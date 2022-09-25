'''
Created by: Atanas Kolev 
First version: 9/9/2020
Second version: 
Bollinger Band + RSI and slope
RSI + slope to identify the trend 
Bollinger Bands to trade when there is no trend
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import datetime as dt
import statsmodels.api as sm


def CAGR(DF):
    "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    n = len(df)/(252*78)
    CAGR = (df["cum_return"].tolist()[-1])**(1/n) - 1
    return CAGR

def volatility(DF):
    "function to calculate annualized volatility of a trading strategy"
    df = DF.copy()
    vol = df["ret"].std() * np.sqrt(252*78)
    return vol

def sharpe(DF,rf):
    "function to calculate sharpe ratio ; rf is the risk free rate"
    df = DF.copy()
    sr = (CAGR(df) - rf)/volatility(df)
    return sr

def max_dd(DF):
    "function to calculate max drawdown"
    df = DF.copy()
    df["cum_return"] = (1 + df["ret"]).cumprod()
    df["cum_roll_max"] = df["cum_return"].cummax()
    df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
    df["drawdown_pct"] = df["drawdown"]/df["cum_roll_max"]
    max_dd = df["drawdown_pct"].max()
    return max_dd

def BolBands(DF, period):
    
    df = DF.copy()
    df['Upper Bound'] = df.rolling(period).mean()['Adj Close'] + (2 * df.rolling(period).std()['Adj Close'])
    df['Lower Bound'] = df.rolling(period).mean()['Adj Close'] - (2 * df.rolling(period).std()['Adj Close'])
    return df

def RSI(DF, win_length):
    df = DF.copy()
    df['delta'] = df['Adj Close'] - df['Adj Close'].shift(1)
    df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
    df['loss'] = np.where(df['delta'] >= 0, df['delta'], 0)
    avg_gain = []
    avg_loss = []
    gain = df['gain'].tolist()
    loss = df['loss'].tolist()
    
    for i in range(len(df)):
        if i < win_length:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == win_length:
            avg_gain.append(df['gain'].rolling(win_length).mean().tolist()[win_length])
            avg_loss.append(df['loss'].rolling(win_length).mean().tolist()[win_length])
        elif i > win_length:
            avg_gain.append(((win_length-1)*avg_gain[i-1] * gain[i])/win_length)
            avg_loss.append(((win_length-1)*avg_loss[i-1] * loss[i])/win_length)
    
    df['avg_gain'] = np.array(avg_gain)
    df['avg_loss'] = np.array(avg_loss)
    df['RS'] = df['avg_gain']/df['avg_loss']
    df['RSI'] = 100 - (100 / (1+df['RS']))
    return df['RSI']

def slope(ser, period):
    
    slopes = [i*0 for i in range(period - 1)]
    for i in range(period, len(ser) + 1):
        y = ser[i-period:i]
        x = np.array(range(period))
        y_scaled = (y - y.min())/(y.max() - y.min())
        x_scaled = (x - x.min())/(x.max() - x.min())
        x_scaled = sm.add_constant(x_scaled)
        model = sm.OLS(y_scaled, x_scaled)
        results = model.fit()
        slopes.append(results.params[-1])
        
    slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
    return np.array(slope_angle)


#1. Getting the data
'''
tickers = ['EURUSD=X', 'GBPUSD=X', 'AUDUSD=X', 'EURGBP=X', 'NZDUSD=X', 'USDCHF=X']
#tickers = ['AAPL', 'MSFT', 'TSLA', 'CSCO']
df_all = pd.DataFrame()
for ticker in tickers:
    df = yf.download(ticker, start = dt.date.today() - dt.timedelta(180), end = dt.date.today(), interval = '1h')
    
'''
df_eur = yf.download('EURUSD=X', dt.date.today() - dt.timedelta(60), dt.date.today(), interval = '1h')
df_gbp = yf.download('GBPUSD=X', dt.date.today() - dt.timedelta(60), dt.date.today(), interval = '1h')
df_aud = yf.download('AUDUSD=X', dt.date.today() - dt.timedelta(60), dt.date.today(), interval = '1h')
df_nzd = yf.download('NZDUSD=X', dt.date.today() - dt.timedelta(60), dt.date.today(), interval = '1h')


#2. Calculating the indicators
df_eur['RSI'] = RSI(df_eur, 20)
df_eur = BolBands(df_eur, 20)
df_eur['Slope'] = slope(df_eur['Adj Close'], 5)

df_gbp['RSI'] = RSI(df_gbp, 20)
df_gbp = BolBands(df_gbp, 20)
df_gbp['Slope'] = slope(df_gbp['Adj Close'], 5)

df_eur['RSI'] = RSI(df_eur, 20)
df_eur = BolBands(df_eur, 20)
df_eur['Slope'] = slope(df_eur['Adj Close'], 5)












































