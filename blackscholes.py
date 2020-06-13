#importing packages, dataframe set-up
import math
import statistics
import numpy as np
import scipy.stats as si
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 1000)

#Black-Scholes Formula - Solving for theoretical option values.
def value(K, T):
    d1 = (np.log(spot / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = (np.log(spot / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    value = (spot * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    return round(value,2)

#K - Returning a list of strike prices, given the stock and date.
def strikes(stock,date):
    option = stock.option_chain(date)
    strike = option.calls["strike"]
    return strike

#T - Representing time until expiration of option in years.
def days_between(d2):
    d1 = datetime.today()
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (abs((d2 - d1).days)/365)

#Approximating market value of option, based on current bids.
def realvalue(K, date):
    option = stock.option_chain(date)
    options = option.calls
    value = options["bid"]
    return value

#creating DataFrame + 3d surface plot
def arraybuild(stock):
    finaldf = pd.DataFrame()
    stock = yf.Ticker(stockinput)
    options = stock.options
    for a in range (len(options)):
        strikelist = ([strikes(stock,options[a])])
        valuelist = ([value(strikes(stock,options[a]), days_between(options[a]))])
        timelist = ([days_between(options[a])])
        realvaluelist = ([realvalue(strikes(stock,options[a]), options[a])])
        df1 = pd.DataFrame(strikelist, index = ["strike"])
        df2 = pd.DataFrame(valuelist, index = ["value"])
        df3 = pd.DataFrame(timelist, index = ["time"])
        df4 = pd.DataFrame(realvaluelist, index = ["bid"])
        df1 = df1.transpose()
        df2 = df2.transpose()
        df3 = df3.transpose()
        df4 = df4.transpose()
        dfsum = pd.concat([df1, df2, df3, df4], axis=1)
        dfsum["time"] = dfsum.iloc[0]["time"]
        finaldf = finaldf.append(dfsum)
    print (finaldf)
    X = finaldf["strike"]
    Z = finaldf["value"]
    Y = finaldf["time"]
    A = finaldf["bid"]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(X, Y, Z, cmap=plt.cm.viridis, linewidth=0.2)
    if bids == 1:
        ax.plot_trisurf(X, Y, A, cmap=plt.cm.inferno, linewidth=0.2)
    ax.set_title('Black-Scholes Theoretical Options Values by Strike/Time')
    ax.set_xlabel('Strike Price')
    ax.set_ylabel('Time to Expiry (years)')
    ax.set_zlabel('Theoretical Value')
    plt.show()

#main
stockinput = input("TICKER>")
if stockinput[-5:] == "+BIDS":
    bids = 1
    stockinput = stockinput[:-5]
else:
    bids = 0
stock = yf.Ticker(stockinput)

#Spot Price - Approximating spot price with last close.
stockdata = stock.history(period="1d")
spot = (stockdata.iloc[0]["Close"])

#Risk-free Rate of Return - Approximated with the annualized return of the 13 week Treasury Bill.
tbill = yf.Ticker("^IRX")
tbill = tbill.history(period="5d")
tbill = (tbill.iloc[-1]["Close"])
r = (1 + tbill / 100) ** 4 - 1

#Sigma/STDEV of Log Returns - Approximated with the standard deviation of one year of daily log returns.
stockhis = stock.history(period="1y")
returns = []
for x in range (len(stockhis)-1):
    p1 = stockhis.iloc[x]["Close"]
    p2 = stockhis.iloc[x+1]["Close"]
    change = math.log(p2/p1)
    returns.append(change)
sigma = (statistics.stdev(returns)*math.sqrt(len(stockhis)))

arraybuild(stock)