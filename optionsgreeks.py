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

#Spot Price - Approximating spot price with last close.
def spotprice(stock):
    stockdata = stock.history(period="1d")
    return stockdata.iloc[0]["Close"]

#Risk-free Rate of Return - Approximated with the annualized return of the 13 week Treasury Bill.
def riskfreerate():
    tbill = yf.Ticker("^IRX")
    tbill = tbill.history(period="5d")
    tbill = (tbill.iloc[-1]["Close"])
    return (1 + tbill / 100) ** 4 - 1

#Sigma/STDEV of Log Returns - Approximated with the standard deviation of one year of daily log returns.
def volatility(stock):
    stockhis = stock.history(period="1y")
    returns = []
    for x in range(len(stockhis) - 1):
        p1 = stockhis.iloc[x]["Close"]
        p2 = stockhis.iloc[x + 1]["Close"]
        change = math.log(p2 / p1)
        returns.append(change)
    return statistics.stdev(returns) * math.sqrt(len(stockhis))

#Finding d1 in Black-Scholes
def d1(K, T):
    return (np.log(spot / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

#Finding d2 in Black-Scholes
def d2(K, T):
    return (np.log(spot / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

#Black-Scholes Formula - Solving for theoretical option values.
def value(K, T):
    value = (spot * si.norm.cdf(d1(K,T), 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2(K,T), 0.0, 1.0))
    return round(value,2)

#Delta - Solving for theoretical delta values.
def delta(K, T):
    delta = si.norm.cdf(d1(K, T), 0.0, 1.0)
    return delta

#Gamma - Solving for theoretical gamma values.
def gamma(K, T):
    gammalist = []
    for x in range (len(K)):
        gamma = (1/(spot*sigma*math.sqrt(T)))*(1/math.sqrt(2*math.pi))*math.exp((-(d1(K[x],T)**2))/2)
        gammalist.append(gamma)
    return gammalist

#Theta - Solving for theoretical theta values.
def theta(K, T):
    thetalist = []
    for x in range (len(K)):
        theta = -((spot*(1/(math.sqrt(2*math.pi)) * math.exp((-(d1(K[x],T))**2)/2))*sigma)/(2*math.sqrt(T)))- (r*K[x]*math.exp(-r*T)*si.norm.cdf(d2(K[x], T), 0.0, 1.0))
        thetalist.append(theta)
    return thetalist

#Vega - Solving for theoretical vega values.
def vega(K, T):
    vegalist = []
    for x in range (len(K)):
        vega = spot*math.sqrt(T)* (1/(math.sqrt(2*math.pi)) * math.exp((-(d1(K[x],T))**2)/2))
        vegalist.append(vega)
    return vegalist

#RHO - Solving for theoretical roe values.
def rho(K, T):
    rholist = []
    for x in range (len(K)):
        rho = K[x]*T*math.exp(-r*T)*si.norm.cdf(d2(K[x], T), 0.0, 1.0)
        rholist.append(rho)
    return rholist

#K - Returning a list of strike prices, given the stock and date.
def strikes(stock,date):
    option = stock.option_chain(date)
    strike = option.calls["strike"]
    return strike

#T - Representing time until expiration of option in years.
def days_between(d2):
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (abs((d2 - datetime.today()).days)/365)


#creating DataFrame + 3d surface plot
def render():
    finaldf = pd.DataFrame()
    stock = yf.Ticker(stockinput)
    options = stock.options
    for a in range (len(options)):
        strikelist = ([strikes(stock,options[a])])
        valuelist = ([value(strikes(stock,options[a]), days_between(options[a]))])
        timelist = ([days_between(options[a])])
        if greek == "DELTA":
            greeklist = ([delta(strikes(stock,options[a]), days_between(options[a]))])
        elif greek == "GAMMA":
            greeklist = ([gamma(strikes(stock,options[a]), days_between(options[a]))])
        elif greek == "THETA":
            greeklist = ([theta(strikes(stock, options[a]), days_between(options[a]))])
        elif greek == "VEGA":
            greeklist = ([vega(strikes(stock, options[a]), days_between(options[a]))])
        elif greek == "RHO":
            greeklist = ([rho(strikes(stock, options[a]), days_between(options[a]))])
        df1 = pd.DataFrame(strikelist, index = ["strike"])
        df2 = pd.DataFrame(valuelist, index = ["value"])
        df3 = pd.DataFrame(timelist, index = ["time"])
        df4 = pd.DataFrame(greeklist, index = [greek])
        df1 = df1.transpose()
        df2 = df2.transpose()
        df3 = df3.transpose()
        df4 = df4.transpose()
        dfsum = pd.concat([df1, df2, df3, df4], axis=1)
        dfsum["time"] = dfsum.iloc[0]["time"]
        finaldf = finaldf.append(dfsum)
    print (finaldf)
    X = finaldf["strike"]
    Z = finaldf[greek]
    Y = finaldf["time"]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(X, Y, Z, cmap=plt.cm.viridis, linewidth=0.2)
    ax.set_title(greek + ' Theoretical Values by Strike/Time')
    ax.set_xlabel('Strike Price')
    ax.set_ylabel('Time to Expiry (years)')
    ax.set_zlabel('Theoretical Value')
    plt.show()

#main
while True:
    tickerinput = input(">")
    if tickerinput[0:6] == "DELTA>":
        greek = "DELTA"
        stockinput = tickerinput[6:]
    elif tickerinput[0:6] == "THETA>":
        greek = "THETA"
        stockinput = tickerinput[6:]
    elif tickerinput[0:6] == "GAMMA>":
        greek = "GAMMA"
        stockinput = tickerinput[6:]
    elif tickerinput[0:5] == "VEGA>":
        greek = "VEGA"
        stockinput = tickerinput[5:]
    elif tickerinput[0:4] == "RHO>":
        greek = "RHO"
        stockinput = tickerinput[4:]

    #establishing variables for Black-Scholes
    stock = yf.Ticker(stockinput)
    spot = spotprice(stock)
    sigma = volatility(stock)
    r = riskfreerate()

    #render
    render()