from scipy.stats import norm
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 30)
pd.set_option('display.max_rows', 500)

index = "^GSPC"
T = 2520
sim_size = 10
start_nav = 100

ticker = yf.Ticker(index)
pricesdf = ticker.history(period="5y")["Close"]
spot = (pricesdf.iloc[len(pricesdf.index)-1])
simulation = pd.DataFrame({"day": np.arange(1, int(T) + 1)})
bulldf = pd.DataFrame({"day": np.arange(1, int(T) + 1)})
beardf = pd.DataFrame({"day": np.arange(1, int(T) + 1)})

returns = (pricesdf - pricesdf.shift(1)) / pricesdf.shift(1)
mu = np.mean(returns.tolist()[1:])
print (mu)
sigma = np.std(returns)

for x in range (sim_size):
    b = np.random.normal(0, 1, int(T))
    w = b.cumsum()
    drift = [(mu - 0.5 * sigma**2) * x for x in simulation["day"]]
    diffusion = (sigma * w)
    sim_price = spot * np.exp(drift + diffusion)
    simulation["sim" + str(x)] = sim_price
simulation = simulation.drop("day", axis=1)
print (simulation)

for x in range (len(list(simulation.columns))):
    ETFbull = [start_nav]
    ETFbear = [start_nav]
    for y in range (T-1):
        assetreturn = (simulation.iloc[y+1][x] - simulation.iloc[y][x]) / simulation.iloc[y][x]
        #newetfprice = ETFbull[len(ETFbull)-1]* (1+assetreturn*3)
        ETFbull.append(ETFbull[len(ETFbull)-1]* (1+assetreturn*3))
        ETFbear.append(ETFbear[len(ETFbear)-1]* (1+assetreturn*-3))
    bulldf["ETF" + str(x)] = ETFbull
    beardf["ETF" + str(x)] = ETFbear
bulldf = bulldf.drop("day", axis=1)
beardf = beardf.drop("day", axis=1)

fig, axs = plt.subplots(nrows = 2, ncols = 1)
simulation.plot.line(y= list(simulation.columns), ax=axs[0], legend=None, figsize=(10,10), grid=True)
#bulldf.plot.line(y= list(bulldf.columns), ax=axs[1],legend=None, figsize=(10,10), ylim = (0,500), grid=True)
beardf.plot.line(y= list(beardf.columns), ax=axs[1],legend=None, figsize=(10,10), ylim = (0,500), grid=True)
plt.show()

