import numpy as np

######################################################################################################################
# HELPER FUNCTIONS
######################################################################################################################

def smoothed_ma(high, low, smoothing_period, future_shift):

    median_prices = ((high + low) / 2).tolist() # high and low are pandas series, hence tolist() converts to python list, so append can be used

    for i in range(smoothing_period, len(high) + future_shift): # starts at smoothing_period, ends at length of high + future_shift
        sum_prices = sum(median_prices[i-smoothing_period:i]) # sum of median_prices at index i - smoothing period to i
        smma = sum_prices / smoothing_period # smoothing the above sum by dividing with smoothing period
        median_prices.append(smma) # appending to median_prices list

    return np.array(median_prices[-(len(high)):]) # return only the smoothed moving averages from the median_prices list


######################################################################################################################
# MAIN FUNCTIONS
######################################################################################################################

def alligator(df, high_col, low_col,
             jaw_smoothing_period, jaw_future_shift,
             teeth_smoothing_period, teeth_future_shift,
             lips_smoothing_period, lips_future_shift):

    df_copy = df.copy() # Copying dataframe to not lose or corrupt any information
 
    if (high_col in df_copy.columns) and (low_col in df_copy.columns): 

        #Jaws is the slowest to react smoothed moving average 
        jaws = smoothed_ma(high = df_copy[high_col], low = df_copy[low_col],
                           smoothing_period=jaw_smoothing_period, future_shift=jaw_future_shift)
        #Teeth is the middle to react smoothed moving average 
        teeth = smoothed_ma(high = df_copy[high_col], low = df_copy[low_col],
                           smoothing_period=teeth_smoothing_period, future_shift=teeth_future_shift)
        #Lips is the fastest to react smoothed moving average 
        lips = smoothed_ma(high = df_copy[high_col], low = df_copy[low_col],
                           smoothing_period=lips_smoothing_period, future_shift=lips_future_shift)

    return jaws, teeth, lips