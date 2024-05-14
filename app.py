import yfinance as yf
from flask import Flask, render_template
import pandas as pd
import requests

import matplotlib.pyplot as plt

app = Flask(__name__)


#in memory cache for the data
data = {}



#add an index rout that will provide links to the tickers 
@app.route('/')
def index():

    # these should be based on percent day gainers and losers
    tickers = getGainLossTickers()
    
    #get info for each one and store in top level dict using get_financial_data
    for ticker in tickers:
        if ticker not in data:
            data[ticker] = get_financial_data(ticker)
    
    #render the template with the tickers and data

    print(data['ADN'].info['insiderColor'])


    return render_template('index.html', tickers=tickers, data=data)

def getGainLossTickers():
    # get the percent gainers and losers
    # url = 'https://query2.finance.yahoo.com/v1/finance/trending/US?count=5&useQuotes=true&fields=logoUrl%2CregularMarketChangePercent%2CregularMarketPrice'
    # headers = {
    #     'accept': '*/*',
    # }
    
    return ['ADN', 'TIRX', 'CTNT', 'SPWR', 'HOLO', 'MAXN', 'KOSS', 'PLUG', 'BIG', 'TUP', 'VUZI', 'SPCE', 'MVIS', 'VUZI', 'PACB', 'HKD', 'DCTH', 'NOVA', 'TMCI', 'BYND']


def get_financial_data(symbol, renderGraphs=False, fetchNews=False):
    stock = yf.Ticker(symbol)

    # Format heldPercentInsiders and heldPercentInstitutions as percentages
    if 'heldPercentInsiders' in stock.info:
        stock.info['heldPercentInsidersDisplay'] = "{:.2%}".format(stock.info['heldPercentInsiders'])
        stock.info['insiderColor'] = 'bg-danger' if  stock.info['heldPercentInsiders'] > .3 else 'bg-warning' if  stock.info['heldPercentInsiders'] > .1 else 'bg-success'

    if 'heldPercentInstitutions' in stock.info:
        stock.info['institutionColor'] = 'bg-danger' if stock.info['heldPercentInstitutions'] > .3 else 'bg-warning' if stock.info['heldPercentInstitutions'] > .1 else 'bg-success'
        stock.info['heldPercentInstitutionsDisplay'] = "{:.2%}".format(stock.info['heldPercentInstitutions'])


    # Set epsColor based on trailingEps
    if 'trailingEps' in stock.info:
        stock.info['epsColor'] = 'bg-success' if stock.info['trailingEps'] < 0 else 'bg-danger'

    # Set employeesColor based on fullTimeEmployees
    if 'fullTimeEmployees' in stock.info:
        stock.info['employeesColor'] = 'bg-danger' if 'fullTimeEmployees' in stock.info and stock.info['fullTimeEmployees'] > 500 else 'bg-warning' if 'fullTimeEmployees' in stock.info and stock.info['fullTimeEmployees'] > 100 else 'bg-success'

    if 'marketCap' in stock.info:
        # Set marketCapColor based on marketCap
        stock.info['marketCapColor'] = 'bg-danger' if stock.info['marketCap'] > 1e9 else 'bg-warning' if stock.info['marketCap'] > 1e8 else 'bg-success'
        stock.info['marketCapDisplay'] = format_large_number(stock.info['marketCap'])


    # Convert nextFiscalYearEnd and mostRecentQuarter to datetime and format as strings
    if 'nextFiscalYearEnd' in stock.info:
        stock.info['nextFiscalYearEndDisplay'] = pd.to_datetime(stock.info['nextFiscalYearEnd'], unit='s').strftime('%Y-%m-%d')

    if 'mostRecentQuarter' in stock.info:
        stock.info['mostRecentQuarterDisplay'] = pd.to_datetime(stock.info['mostRecentQuarter'], unit='s').strftime('%Y-%m-%d')


    # Make a line chart of the daily stock price over the last year
    hist = stock.history(period="1y")
    hist['Date'] = hist.index.strftime('%Y-%m-%d')
    hist['Close'] = hist['Close'].astype(float)

    if renderGraphs:
        plt.figure(figsize=(7, 4))
        plt.plot(hist['Date'], hist['Close'])
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
        plt.title(symbol + ' Closing Price (Last 1 year)')
        plt.xticks(hist['Date'][::50], rotation=45)
        plt.tight_layout()
        plt.savefig('static/last_year.png')
        plt.close()

        # Make a line plot of the 5 min intervals
        intraday = stock.history(period="1d", interval="5m")
        intraday['Date'] = intraday.index.strftime('%H:%M')
        intraday['Close'] = intraday['Close'].astype(float)

        plt.figure(figsize=(7, 4))
        plt.plot(intraday['Date'], intraday['Close'])
        plt.xlabel('Time')
        plt.ylabel('Closing Price')
        plt.title(symbol + ' Price (5 min intervals)')
        plt.xticks(intraday['Date'][::50], rotation=45)
        plt.tight_layout()
        plt.savefig('static/intraday.png')
        plt.close()

    if fetchNews:
        # Format the news publish date
        for news in stock.news:
            news['providerPublishTimeDisplay'] = pd.to_datetime(news['providerPublishTime'], unit='s').strftime('%Y-%m-%d %H:%M')

    return stock



@app.route('/<symbol>')
def financial_data(symbol):

    # Get the financial data for the stock
    stock = get_financial_data(symbol, True, True)

    # Render the template with the financial data
    return render_template('financial_data.html', data=stock.info, news=stock.news)

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
