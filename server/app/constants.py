# SCALARS
close_col = 'Close'
close_shifted_col = 'Close_Shifted'
delta = 'delta'
gain = 'gain'
loss = 'loss'
avg_gain = 'avg_gain'
avg_loss = 'avg_loss'
upper_bound = 'upper_bound'
lower_bound = 'lower_bound'
rolling_mean = 'rolling_mean_'
RS = 'RS'
RSI = 'RSI'
slope = 'slope'
default_ticker = 'AAPL'
default_period_back = 'max'
default_interval = '1d'
default_period_BB = 20
default_win_length_RSI = 20
default_period_slope = 5
default_close_shifted_tolerance = 0.005
signal_from_bb = 'signal_from_bb'
price_change_up = 'price_change_up'
price_change_down = 'price_change_down'
slope_cat_col = 'slope_cat'
label = 'Close_Shifted'
pred_col_name = 'predictions'
predicted_diff_col = 'predicted_diff'
predicted_change_col = 'predicted_change'


# LISTS
f_cols = ['Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits', 'upper_bound', 'lower_bound', 'rolling_mean_20', 'slope']



# DICTS
model_params = {'max_depth' : 2,
                'gamma' : 5,
                'eta' : 0.2,
                'subsample' : 0.75}