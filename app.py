import yfinance as yf
from flask import Flask, render_template, request
import pandas as pd
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt

app = Flask(__name__)


#in memory cache for the data
data = {}

#add an index rout that will provide links to the tickers 
@app.route('/')
def index():

    # these should be based on percent day gainers and losers
    tickers = getHalts()

    
    #get info for each one and store in top level dict using get_financial_data
    for ticker in tickers:
        if ticker not in data:
            data[ticker] = get_financial_data(ticker)
            data[ticker].info['bg'] = 'bg-unset'
    
    #render the template with the tickers and data
    return render_template('index.html', tickers=tickers, data=data)

# def getPreMarketMovers():
#     #make request to the site using selenium headless
#     url = 'https://www.tradingview.com/markets/stocks-usa/market-movers-pre-market-gainers/'

#     chrome_options = Options()
#     chrome_options.add_argument("--headless")

#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(url)

#     sleep(2)

#     table = driver.find_element("xpath","//*[@id='pageContainer']/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div


def getHalts():
    #make request to the site using selenium headless
    url = 'https://www.nasdaqtrader.com/trader.aspx?id=tradehalts'

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    sleep(2)

    table = driver.find_element("xpath","//*[@id='divTradeHaltResults']")

    #parse the table
    rows = table.find_elements(by=By.TAG_NAME, value="tr")


    #skip the header row, get the tickers by looking at the third 'td' in each row
    tickerList = []
    for row in rows[1:]:
        ticker = row.find_elements(by=By.TAG_NAME, value="td")[2].text
        #if the ticker has '.' or '=' skip it, also only add if it's not already in the list
        if '.' not in ticker and '=' not in ticker and ticker not in tickerList:
            tickerList.append(ticker)


    return tickerList

def get_financial_data(symbol, renderGraphs=False):
    stock = yf.Ticker(symbol)

    # Format heldPercentInsiders and heldPercentInstitutions as percentages
    if 'heldPercentInsiders' in stock.info:
        stock.info['heldPercentInsidersDisplay'] = "{:.2%}".format(stock.info['heldPercentInsiders'])
        stock.info['insiderColor'] = 'bg-red-500' if  stock.info['heldPercentInsiders'] > .3 else 'bg-yellow-500' if  stock.info['heldPercentInsiders'] > .1 else 'bg-green-500'

    if 'heldPercentInstitutions' in stock.info:
        stock.info['institutionColor'] = 'bg-red-500' if stock.info['heldPercentInstitutions'] > .3 else 'bg-yellow-500' if stock.info['heldPercentInstitutions'] > .1 else 'bg-green-500'
        stock.info['heldPercentInstitutionsDisplay'] = "{:.2%}".format(stock.info['heldPercentInstitutions'])


    # Set epsColor based on trailingEps
    if 'trailingEps' in stock.info:
        stock.info['epsColor'] = 'bg-green-500' if stock.info['trailingEps'] < 0 else 'bg-red-500'

    # Set employeesColor based on fullTimeEmployees
    if 'fullTimeEmployees' in stock.info:
        stock.info['employeesColor'] = 'bg-red-500' if 'fullTimeEmployees' in stock.info and stock.info['fullTimeEmployees'] > 500 else 'bg-yellow-500' if 'fullTimeEmployees' in stock.info and stock.info['fullTimeEmployees'] > 100 else 'bg-green-500'

    if 'marketCap' in stock.info:
        # Set marketCapColor based on marketCap
        stock.info['marketCapColor'] = 'bg-red-500' if stock.info['marketCap'] > 1e9 else 'bg-yellow-500' if stock.info['marketCap'] > 1e8 else 'bg-green-500'
        stock.info['marketCapDisplay'] = format_large_number(stock.info['marketCap'])


    # Convert nextFiscalYearEnd and mostRecentQuarter to datetime and format as strings
    if 'nextFiscalYearEnd' in stock.info:
        stock.info['nextFiscalYearEndDisplay'] = pd.to_datetime(stock.info['nextFiscalYearEnd'], unit='s').strftime('%Y-%m-%d')

    if 'mostRecentQuarter' in stock.info:
        stock.info['mostRecentQuarterDisplay'] = pd.to_datetime(stock.info['mostRecentQuarter'], unit='s').strftime('%Y-%m-%d')


    # Make a line chart of the daily stock price over the last year
    hist = stock.history(period="ytd")
    hist['Close'] = hist['Close'].astype(float)

    
    hist['Date'] = pd.to_datetime(hist.index).strftime('%Y-%m-%d')
    plt.figure(figsize=(7, 4))
    plt.plot(hist['Date'], hist['Close'])
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title(symbol + ' Closing Price (Last 1 year)')
    # plt.xticks(hist['Date'][::50], rotation=45)
    plt.tight_layout()

    #make a directory for the stock if it doesn't exist
    import os
    if not os.path.exists('static/'+symbol):
        os.makedirs('static/'+symbol)


    plt.savefig('static/'+ symbol +'/last_year.png')
    plt.close()

    # Make a line plot of the 5 min intervals
    intraday = stock.history(period="1d", interval="5m")
    intraday['Date'] = pd.to_datetime(intraday.index).strftime('%H:%M')
    intraday['Close'] = intraday['Close'].astype(float)

    plt.figure(figsize=(7, 4))
    plt.plot(intraday['Date'], intraday['Close'])
    plt.xlabel('Time')
    plt.ylabel('Closing Price')
    plt.title(symbol + ' Price (5 min intervals)')
    
    plt.tight_layout()
    plt.savefig('static/'+symbol+'/intraday.png')
    plt.close()

    # Format the news publish date
    for news in stock.news:
        news['providerPublishTimeDisplay'] = pd.to_datetime(news['providerPublishTime'], unit='s').strftime('%Y-%m-%d %H:%M')

    return stock



@app.route('/<symbol>')
def financial_data(symbol):

    # Get the financial data for the stock
    stock = get_financial_data(symbol, True)

    # Render the template with the financial data
    return render_template('financial_data.html', data=stock.info, news=stock.news)

# # define PUT /<symbol> to update the data for a given ticker
# @app.route('/<symbol>', methods=['PUT'])
# def update_financial_data(symbol):
#     updateData = request.get_json(force=True)
#     print(updateData)

#     if symbol in data:
#         data[symbol].info['bg'] = updateData['status']
#     else:
#         data[symbol] = get_financial_data(symbol)
#         data[symbol].info['bg'] = updateData['status']
#     return "OK"


def format_large_number(num):
    if num >= 1_000_000_000:
        formatted_num = f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        formatted_num = f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        formatted_num = f"{num / 1_000:.1f}K"
    else:
        formatted_num = str(num)
    return formatted_num

if __name__ == "__main__":
    app.run()
