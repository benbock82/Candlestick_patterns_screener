"""
This app is to screen the selected stocks from russell 1000 index.

"""

import mplfinance as mpf
import pandas as pd
import streamlit as st
import talib
import yfinance as yf


# create a function to load russell_1000 stock symbol as variable
def create_russell_1000_symbol():
    russell_1000 = pd.read_csv('Stocks in the Russell 1000 Index.csv')
    russell_1000_symbol = russell_1000['Symbol']
    return russell_1000_symbol


# create a function to load stock data from yfinance and create open, high, low and close variables
@st.cache
def load_stock_data(symbol, period, interval):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    op, hi, lo, cl = df['Open'], df['High'], df['Low'], df['Close']
    return op, hi, lo, cl


# Define function to append values to dictionary
def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value


# Define function to screen the stocks with the candlestick patterns
def screen_pattern(selected_pattern, state):
    # result is according to the selected pattern
    result = getattr(talib, selected_pattern)(op, hi, lo, cl)
    # Candlestick patterns which are bullish has result 100 or 200
    if result[-1] >= 100 and state == 'Bullish':
        # found_pattern_info.append(f"{symbol} : {state} {candle[3::]}")
        append_value(found_pattern_info, symbol, f'{state} {candle[3::]}')
        found_pattern_symbol.append(symbol)
    # Candlestick patterns which are bullish has result -100 or -200
    elif result[-1] <= -100 and state == 'Bearish':
        # found_pattern_status.append(f"{symbol} : {state} {candle[3::]}")
        append_value(found_pattern_info, symbol, f'{state} {candle[3::]}')
        found_pattern_symbol.append(symbol)


# Create the title for this app
st.title('Candlestick patterns stock screener')

# Create a variable for watchlist
watch_list = st.multiselect(
    'Please select the ticker(s) from russell 1000 index which you wish to scan for candlestick pattern',
    create_russell_1000_symbol())

# Create option for the trading timeframe
trading_timeframe = st.selectbox('Trading Time Frame', ('month', 'week', 'day', '60 min', '15 min', '5 min', '1 min'))

if trading_timeframe == 'month':
    period = '1y'
    interval = '1mo'
    chart_period = '5y'
    chart_interval = '1mo'
elif trading_timeframe == 'week':
    period = '3mo'
    interval = '1w'
    chart_period = '2y'
    chart_interval = '1w'
elif trading_timeframe == 'day':
    period = '1mo'
    interval = '1d'
    chart_period = '6mo'
    chart_interval = '1d'
elif trading_timeframe == '60 min':
    period = '1d'
    interval = '60m'
    chart_period = '5d'
    chart_interval = '60m'
elif trading_timeframe == '15 min':
    period = '1d'
    interval = '15m'
    chart_period = '1d'
    chart_interval = '15m'
elif trading_timeframe == '5 min':
    period = '1d'
    interval = '5m'
    chart_period = '1d'
    chart_interval = '5m'
else:
    period = '1d'
    interval = '1m'
    chart_period = '1d'
    chart_interval = '1m'

# Create candlestick pattern names variable
candle_names = talib.get_function_groups()['Pattern Recognition']

# Create the states variable (Bullish and Bearish)
states = ['Bullish', 'Bearish']

# Create empty list and dict to store the result
found_pattern_symbol = []
found_pattern_info = {}
my_bar = st.progress(0)
progress = 0

if st.button('Please click here to proceed the screening'):
    # Create for loop to screen through the stocks for candlestick patterns
    for symbol in watch_list:
        op, hi, lo, cl = load_stock_data(symbol, period=period, interval=interval)
        for state in states:
            for candle in candle_names:
                try:
                    screen_pattern(candle, state)
                except:
                    pass
        progress += 1 / len(watch_list)
        my_bar.progress(progress)
found_pattern_symbol = tuple(set(found_pattern_symbol))
st.subheader('Candlestick patterns found')
st.write('Stock with candlestick pattern found', found_pattern_symbol)
st.write('Stock candlestick patterns', found_pattern_info)

st.subheader('Charts')
st.write(f'Period: {chart_period}')
st.write(f'Interval: {chart_interval}')
st.write('candlestick chart with 20 intervals simple moving average')
for chart_symbol in found_pattern_symbol:
    ticker = yf.Ticker(chart_symbol)
    df_chart = ticker.history(period=chart_period, interval=chart_interval)
    fig, ax = mpf.plot(df_chart, type='candle', figsize=(20, 10),
                       title=f'Stock symbol: {chart_symbol}\nCandlestick pattern(s): {found_pattern_info[chart_symbol]}',
                       mav=20,
                       volume=True, returnfig=True)
    st.pyplot(fig)
