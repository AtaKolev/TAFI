import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
import constants as const

def download_ticker(ticker:str, period_back, interval:str):
    '''
    ticker : data for what to download
    start_date : when to start the data
    end_date : when to end the data
    interval : '1h', '1m' ... self-explanatory
    '''
    ticker_obj = yf.Ticker(ticker)
    ticker_df = ticker_obj.history(period_back, interval = interval)

    return ticker_df

def BolBands(df, period):
    
    upper_bound = df.rolling(period).mean()[const.close_col] + (2 * df.rolling(period).std()[const.close_col])
    lower_bound = df.rolling(period).mean()[const.close_col] - (2 * df.rolling(period).std()[const.close_col])
    rolling_mean = df.rolling(period).mean()[const.close_col]

    return upper_bound, lower_bound, rolling_mean

def RSI(DF, win_length):
    df = DF.copy()
    df[const.delta] = df[const.close_col] - df[const.close_col].shift(1)
    df[const.gain] = np.where(df[const.delta] >= 0, df[const.delta], 0)
    df[const.loss] = np.where(df[const.delta] >= 0, df[const.delta], 0)
    avg_gain = []
    avg_loss = []
    gain = df[const.gain].tolist()
    loss = df[const.loss].tolist()
    
    for i in range(len(df)):
        if i < win_length:
            avg_gain.append(np.NaN)
            avg_loss.append(np.NaN)
        elif i == win_length:
            avg_gain.append(df[const.gain].rolling(win_length).mean().tolist()[win_length])
            avg_loss.append(df[const.loss].rolling(win_length).mean().tolist()[win_length])
        elif i > win_length:
            avg_gain.append(((win_length-1)*avg_gain[i-1] * gain[i])/win_length)
            avg_loss.append(((win_length-1)*avg_loss[i-1] * loss[i])/win_length)
    
    df[const.avg_gain] = np.array(avg_gain)
    df[const.avg_loss] = np.array(avg_loss)
    df[const.RS] = df[const.avg_gain]/df[const.avg_loss]
    df[const.RSI] = 100 - (100 / (1+df['RS']))
    return df[const.RSI]

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

def main_pipe(ticker = const.default_ticker, period_back = const.default_period_back, interval = const.default_interval, 
              period_BB = const.default_period_BB, win_length_RSI = const.default_win_length_RSI, period_slope = const.default_period_slope,
              close_shifted_tolerance = const.default_close_shifted_tolerance):

    main_df = download_ticker(ticker, period_back, interval)
    main_df[const.upper_bound], main_df[const.lower_bound], main_df[const.rolling_mean + f'_{period_BB}'] = BolBands(main_df, period_BB)
    main_df[const.RSI] = RSI(main_df, win_length_RSI)
    main_df[const.slope] = slope(main_df[const.close_col], period_slope)
    main_df[const.close_shifted_col] = main_df[const.close_col].shift(-1).fillna(0)
    main_df['Price_change'] = np.where(main_df[const.close_col] > (main_df[const.close_shifted_col] + (main_df[const.close_col] * 0.05)), 1,
                                       np.where((main_df[const.close_col] <= (main_df[const.close_shifted_col] + (main_df[const.close_col] * close_shifted_tolerance))) & (main_df[const.close_col] > (main_df[const.close_shifted] - (main_df[const.close_col] * close_shifted_tolerance))), 0,
                                                np.where(main_df[const.close_col] < (main_df[const.close_shifted_col] - (main_df[const.close_col] * 0.05)), -1, 2)))

    return main_df