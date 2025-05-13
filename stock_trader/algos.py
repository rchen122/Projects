from file_and_graph import *
import numpy as np

in_trade, already_traded = False, False

def take_profit(entry_price, current_price, trend, target, risk):
    if trend is True and current_price - entry_price > target: #uptrend and reached profit target
        return calculate_profit(entry_price, current_price, not trend)
    # elif trend is True and entry_price - current_price > risk: # uptrend but current price dropped and reached risk tolerance
    #     return calculate_profit(entry_price, current_price, not trend)
    elif trend is False and entry_price - current_price > target: # downtrend and reached profit target
        return calculate_profit(entry_price, current_price, not trend)
    # elif trend is False and entry_price - current_price > -risk: # downtrend but current price went up and reached risk tolerance
    #     return calculate_profit(entry_price, current_price, not trend)

    return None

def calculate_profit(entry_price, exit_price, trend):
    #if trend is True, then changed from downtrend to uptrend
    # if trend is False, changed from uptrend to downtrend
    price_change = round(exit_price - entry_price, 2)
    return price_change * 1 if trend is False else price_change * -1

def SMA_crossing(date, df, SMAs, target, risk): # only valid for one trade per day
    """
    Tests the SMA crossing strategy on recently passed dates.

    Args: 
        date: the date of the df that we have for the data
        df: information on stock prices for that day
        SMAs: the pair of SMA lengths to test
        target: Target Profit
        risk: risk tolerance
    Returns:
        Profit: profit amount
        entry_time: time of trade entry
        exit_time: time of trade exit

    """

    val_iter = df.loc[f"{date} 04:00:00":f"{date} 09:25:00"] # extended hours
    short_tf = val_iter[f"SMA_{min(SMAs)}"].iloc[-1]
    long_tf = val_iter[f"SMA_{max(SMAs)}"].iloc[-1]
    uptrend = True if short_tf - long_tf >= 0 else False # positive means uptrend
    entry_price = entry_time = None
    exit_price = exit_time = None
    in_trade = False
    for time_int in df.loc[f"{date} 09:30:00":f"{date} 16:00:00"].index: # iterate each time interval to immidate blind future values
        val_iter = pd.concat([val_iter, df.loc[time_int].to_frame().T])
        short_tf = val_iter[f"SMA_{min(SMAs)}"].iloc[-1]
        long_tf = val_iter[f"SMA_{max(SMAs)}"].iloc[-1]
        trend = True if short_tf - long_tf >= 0 else False # positive means uptrend

        if in_trade is True:
            profit = take_profit(entry_price, val_iter["4. close"].iloc[-1], trend, target, risk)
            if profit is not None:
                # print(trend, val_iter["4. close"].iloc[-1] - entry_price, profit_con)
                exit_time = val_iter["4. close"].index[-1].strftime("%H:%M")
                exit_price = val_iter["4. close"].iloc[-1]
                return profit, entry_time, entry_price, exit_time, exit_price
        if trend is not uptrend:
            # print(f"Changed to uptrend at {time_int}") if trend is True else print(f"Changed to downtrend at {time_int}")
            if in_trade is False:
                entry_price = val_iter["4. close"].iloc[-1]
                entry_time = val_iter["4. close"].index[-1].strftime("%H:%M")
                in_trade = True
            else:
                exit_price = val_iter["4. close"].iloc[-1]
                profit = calculate_profit(entry_price, exit_price, trend)
                exit_time = val_iter["4. close"].index[-1].strftime("%H:%M")
                # print(entry_price, exit_price, profit)
                return profit, entry_time, entry_price, exit_time, exit_price
            uptrend = trend
    return 0, None, None, None, None


    