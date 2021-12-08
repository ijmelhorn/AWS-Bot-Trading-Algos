def get_price(asset,from_date_var,to_date_var,interval_var):
    """
    function geared towards fetching crypto asset prices for a time period
    example call: get_price('bitcoin','2017-01-01','2021-12-01','1d')    
    """
    import san 
    import pandas as pd
    import finta as f
    pd.options.display.float_format = '{:.2f}'.format
    

    df = san.get(
        "ohlcv/"+asset,
        from_date="2018-12-01",
        to_date="2021-12-01",
        interval="1d")

    rename={"openPriceUsd":"open",	"closePriceUsd":"close",	"highPriceUsd":"high",	"lowPriceUsd":"low"}
    df.rename(columns=rename,inplace=True)

    df["actual_returns"] = df["close"].pct_change()

    # Drop all NaN values from the DataFrame
    df = df.dropna()



    return df


def get_sma(signals_df,short_window,long_window):
    from finta import TA

    
    signals_df["sma_fast"] = TA.SMA(signals_df, short_window)
    signals_df["sma_slow"] = TA.SMA(signals_df, long_window)
    return signals_df.dropna()

def create_golden_cross_signal_df(trading_df,short_window_var,long_window_var):
    
    import numpy as np
    signals_df=trading_df.copy()
    # Set the short window and long windows
    short_window = 50
    long_window = 200

    # Add the SMA technical indicators for the short and long windows
    get_sma(signals_df,short_window,long_window)

    # Set the Signal column
    signals_df["Signal"] = 0.0

    # Generate the trading signal 1 or 0,
    # where 1 is when the Short window is greater than (or crosses over) the Long Window
    # where 0 is when the Short window is under the Long window
    signals_df["Signal"][short_window:] = np.where(
        signals_df["sma_fast"][short_window:] > signals_df["sma_slow"][short_window:], 1.0, 0.0
    )

    # Calculate the points in time at which a position should be taken, 1 or -1
    signals_df["Entry/Exit"] = signals_df["Signal"].diff()

    return signals_df

def get_BBbands(signals_df):
    import pandas as pd
    import finta as f
    return pd.concat([signals_df,f.TA.BBANDS(signals_df)],axis=1).dropna()


def plot_entries_exits(signals_df, column_of_e_n_x):
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    signals_df= signals_df.copy()
    # Visualize entry position relative to close price
    entry = signals_df[signals_df[column_of_e_n_x] == 1.0]["close"].hvplot.scatter(
        color='purple',
        marker='^',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize exit position relative to close price
    exit = signals_df[signals_df[column_of_e_n_x] == -1.0]["close"].hvplot.scatter(
        color='orange',
        marker='v',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize close price for the investment
    security_close = signals_df[["close"]].hvplot(
        line_color='lightgray',
        ylabel='Price in $',
        width=1000,
        height=400
    )

 
    # Overlay plots
    entry_exit_plot = security_close  * entry * exit
    return entry_exit_plot

def get_RSI_decision(RSI,loc_min,loc_max,RSI_BUY_TRIGGERVAR,RSI_SELL_TRIGGERVAR):
   
    if RSI>=RSI_SELL_TRIGGERVAR and loc_max!=0:
        return -1
    elif RSI<=RSI_BUY_TRIGGERVAR and loc_min!=0:
        return 1
    else:
        return 0

def get_RSI_signal_df(signals_df_var,period_var,column_var,adjust_var,order_of_neigboring_periods):
    import pandas as pd
    import numpy as np
    import hvplot.pandas
    from pathlib import Path
    import matplotlib.pyplot as plt
    from scipy.signal import argrelextrema
    import finta as f
    

    signals_df=signals_df_var.copy()
    signals_df['RSI']=f.TA.RSI(signals_df,period_var,column_var,adjust_var)
    loc_min = argrelextrema(signals_df.close.values, np.less_equal,order=order_of_neigboring_periods)
    loc_max = argrelextrema(signals_df.close.values, np.greater_equal,order=order_of_neigboring_periods)
    signals_df['loc_min'] = signals_df.close.iloc[loc_min]
    signals_df['loc_max'] = signals_df.close.iloc[loc_max]
    signals_df.loc_min[signals_df.loc_min.isnull()]=0
    signals_df.loc_max[signals_df.loc_max.isnull()]=0
    #get the mean RSI for local maxima and minima
    RSI_SELL_TRIGGER = signals_df[signals_df.loc_max>0].loc[:,'RSI'].mean()
    RSI_BUY_TRIGGER  = signals_df[signals_df.loc_min>0].loc[:,'RSI'].mean()
    signals_df['RSI_signal']=signals_df.apply( lambda x: get_RSI_decision(x['RSI'],x['loc_min'],x['loc_max'],RSI_SELL_TRIGGERVAR=RSI_SELL_TRIGGER,RSI_BUY_TRIGGERVAR=RSI_BUY_TRIGGER),axis=1)
    signals_df['Entry/Exit']=signals_df.RSI_signal.diff()
    #print(signals_df.head())
    #signals_df["RSI_Entry/Exit"] = signals_df["RSI_Signal"].diff()
    return signals_df.dropna()

def plot_entry_exits(signals_df,column):
    plot_of_entries=0
    return plot_of_entries

def plot_golden_cross(signals_df):

    import hvplot.pandas

        # Visualize entry position relative to close price
    entry = signals_df[signals_df["Entry/Exit"] == 1.0]["close"].hvplot.scatter(
        color='purple',
        marker='^',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize exit position relative to close price
    exit = signals_df[signals_df["Entry/Exit"] == -1.0]["close"].hvplot.scatter(
        color='orange',
        marker='v',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize close price for the investment
    security_close = signals_df[["close"]].hvplot(
        line_color='lightgray',
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize moving averages
    moving_avgs = signals_df[["sma_fast", "sma_slow"]].hvplot(
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Overlay plots
    entry_exit_plot = security_close * moving_avgs * entry * exit
    
    return entry_exit_plot

def get_bb_signal(bb_signals_df):
    bb_signals_df["Signal"] = 0.0

    # Generate the trading signals 1 (entry) or -1 (exit) for a long position trading algorithm
    # where 1 is when the Close price is less than the BB_LOWER window
    # where -1 is when the Close price is greater the the BB_UPPER window
    for index, row in bb_signals_df.iterrows():
        if row["close"] < row["BB_LOWER"]:
            bb_signals_df.loc[index, "Signal"] = 1.0
        if row["close"] > row["BB_UPPER"]:
            bb_signals_df.loc[index,"Signal"] = -1.0
    
  
    
    return bb_signals_df

def update_bb_entries_exit(bb_signals_df):
    # Update the trading algorithm using Bollinger Bands

    # Set the Signal column
    bb_signals_df["Signal"] = 0.0

    # Create a value to hold the initial trade signal
    trade_signal = 0

    # Update the DataFrame Signal column 1 (entry) or -1 (exit) for a long position trading algorithm
    # where 1 is when the Close price is less than the BB_LOWER window
    # where -1 is when the Close price is greater the the BB_UPPER window
    # Incorporate a conditional in the if-statement, to evaluate the value of the trade_signal so the algorithm 
    # plots only 1 entry and exit point per cycle.
    for index, row in bb_signals_df.iterrows():
        if (row["close"] < row["BB_LOWER"]) and (trade_signal < 1):
            bb_signals_df.loc[index, "Signal"] = 1.0
            trade_signal += 1
            
        if (row["close"] > row["BB_UPPER"]) and (trade_signal > 0):
            bb_signals_df.loc[index, "Signal"] = -1.0
            trade_signal = 0

    return bb_signals_df
    
def plot_bb_decision(bb_signals_df,signalCol):

    
        # Visualize entry position relative to close price
    entry = bb_signals_df[bb_signals_df[signalCol] == 1.0]["close"].hvplot.scatter(
        color='green',
        marker='^',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize exit position relative to close price
    exit = bb_signals_df[bb_signals_df[signalCol] == -1.0]["close"].hvplot.scatter(
        color='red',
        marker='v',
        size=200,
        legend=False,
        ylabel='Price in $',
        width=1000,
        height=400
    )

    # Visualize close price for the investment
    security_close = bb_signals_df[["close"]].hvplot(
        line_color='lightgray',
        ylabel='Price in $',
        width=1000,
        height=400
    )

    bb_upper = bb_signals_df[["BB_UPPER"]].hvplot(
        line_color='purple',
        ylabel='Price in $',
        width=1000,
        height=400
    )


    bb_middle = bb_signals_df[["BB_MIDDLE"]].hvplot(
        line_color='orange',
        ylabel='Price in $',
        width=1000,
        height=400
    )

    bb_lower = bb_signals_df[["BB_LOWER"]].hvplot(
        line_color='blue',
        ylabel='Price in $',
        width=1000,
        height=400
    )


    # Overlay plots
    bbands_plot = security_close * bb_upper * bb_middle * bb_lower * entry * exit
    
    return bbands_plot