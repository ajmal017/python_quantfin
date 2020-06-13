#packages
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 500)
total_payoff = 0

#function INFO:
def info(stock):
    stockinput = yf.Ticker(stock)
    print ("Ticker:", stock, "\n", stockinput.history(period="0"))

#function CHAIN:
def chain(stock):
    stockinput = yf.Ticker(stock)
    print ("\nOptions Dates:", stockinput.options)
    date = input("DATE:")
    option = stockinput.option_chain(date)
    optionschain = pd.merge(option.calls, option.puts, on='strike')
    optionschain = optionschain.drop(columns=['lastTradeDate_x', 'change_x', 'percentChange_x', 'volume_x', 'openInterest_x', 'impliedVolatility_x', 'contractSize_x','currency_x', 'contractSymbol_y', 'lastTradeDate_y', 'change_y', 'percentChange_y', 'volume_y', 'openInterest_y', 'impliedVolatility_y', 'contractSize_y', 'currency_y', 'inTheMoney_y'])
    print (optionschain)

#function CALL:
def call(stock):
    spot_price = spot(stock)
    sT = np.arange(0.7 * spot_price, 1.3 * spot_price, 1)
    returndata = optionsdata(stock,"CALL")
    premium = returndata[0]
    strike = returndata[1]
    long_short = input("LONG/SHORT>")
    if long_short == "LONG":
        payoff_long_call = np.where(sT > strike, sT - strike, 0) - premium
        new_payoff = render(total_payoff, payoff_long_call, sT, spot_price)
    elif long_short == "SHORT":
        payoff_short_call = -(np.where(sT > strike, sT - strike, 0) - premium)
        new_payoff = render(total_payoff, payoff_short_call, sT, spot_price)
    return (new_payoff)

#function PUT:
def put(stock):
    spot_price = spot(stock)
    sT = np.arange(0.7 * spot_price, 1.3 * spot_price, 1)
    returndata = optionsdata(stock, "PUT")
    premium = returndata[0]
    strike = returndata[1]
    long_short = input("LONG/SHORT>")
    if long_short == "LONG":
        payoff_long_put = np.where(sT < strike, strike - sT, 0) - premium
        new_payoff = render(total_payoff, payoff_long_put, sT, spot_price)
    if long_short == "SHORT":
        payoff_short_put = -(np.where(sT < strike, strike - sT, 0) - premium)
        new_payoff = render(total_payoff, payoff_short_put, sT, spot_price)
    return (new_payoff)

#function STOCK
def stock(stock):
    spot_price = spot(stock)
    sT = np.arange(0.7 * spot_price, 1.3 * spot_price, 1)
    long_short = input("LONG/SHORT>")
    if long_short == "LONG":
        payoff_long_stock = sT - spot_price
        new_payoff = render(total_payoff, payoff_long_stock, sT, spot_price)
    elif long_short == "SHORT":
        payoff_short_stock = spot_price - sT
        new_payoff = render(total_payoff, payoff_short_stock, sT, spot_price)
    return (new_payoff)

#premium lookup
def optionsdata(stock,option_type):
    date = input("EXP>")
    strike = float(input("STRIKE>"))
    stockinput = yf.Ticker(stock)
    chain = stockinput.option_chain(date)
    if option_type == "CALL":
        calls = chain.calls
        row_number = calls[calls["strike"] == strike].index
        premium = float(calls.iloc[row_number]["lastPrice"])
    elif option_type == "PUT":
        puts = chain.puts
        row_number = puts[puts["strike"] == strike].index
        premium = float(puts.iloc[row_number]["lastPrice"])
    return (premium,strike)

#spot_price lookup
def spot(stock):
    stockhistory = stockinput.history(period="0")
    spot_price = stockhistory.iloc[0]["Close"]
    return(spot_price)

#render
def render(total_payoff, payoff, sT, spot_price):
    total_payoff = total_payoff + payoff
    fig, ax = plt.subplots()
    ax.spines['bottom'].set_position('zero')
    ax.plot(sT, total_payoff)
    plt.axvline(x=spot_price, label='Spot Price', color = 'lightgray')
    plt.xlabel('Stock Price')
    plt.ylabel('Profit and loss')
    plt.legend()
    plt.show()
    return (total_payoff)

#main
payoff = 0
print ("OPTIONS PAYOFF GRAPH VISUALIZER","\nFUNCTIONS:", "\n INFO>[STOCK] : Provides latest market pricing for [STOCK]", "\n CHAIN>[STOCK] : Provides option chain for [STOCK]", "\n STOCK>[STOCK] : Start a LONG/SHORT position.", "\n CALL>[STOCK] : Purchase or sell a call option.", "\n PUT>[STOCK] : Purchase or sell a put option.")
while True:
    command = input("> ")
    if command[0:5] == "INFO>":
        info(command[5:])
    elif command[0:6] == "CHAIN>":
        chain(command[6:])
    elif command[0:5] == "CALL>" or command[0:4] == "PUT>" or command[0:6] == "STOCK>":
        if command[0:5] == "CALL>":
            stockinput = yf.Ticker(command[5:])
            total_payoff = call(command[5:])
        elif command[0:4] == "PUT>":
            stockinput = yf.Ticker(command[4:])
            total_payoff = put(command[4:])
        elif command[0:6] == "STOCK>":
            stockinput = yf.Ticker(command[6:])
            total_payoff = stock(command[6:])