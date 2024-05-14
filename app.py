import sys
import yfinance as yf
from flask import Flask, render_template
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/ticker/<symbol>')
def get_financial_data(symbol):
    stock = yf.Ticker(symbol)

    # heldPercentInsiders and heldPercentInstitutions are in scientific notation, they should be converted to strings and displayed as percentages
    stock.info['heldPercentInsidersDisplay'] = "{:.2%}".format(stock.info['heldPercentInsiders'])
    stock.info['heldPercentInstitutionsDisplay'] = "{:.2%}".format(stock.info['heldPercentInstitutions'])

        #     <!-- if data.heldPercentInsiders > .3 color card light red -->
        # <!-- if .1 < data.heldPercentInsiders < .3 color card light yellow -->
        # <!-- if data.heldPercentInsiders < .1 color card light green -->

    if stock.info['heldPercentInsiders'] > .3:
        stock.info['insiderColor'] = 'bg-danger'
    elif stock.info['heldPercentInsiders'] > .1:
        stock.info['insiderColor'] = 'bg-warning'
    else:
        stock.info['insiderColor'] = 'bg-success'

    #same for institutions
    if stock.info['heldPercentInstitutions'] > .3:
        stock.info['institutionColor'] = 'bg-danger'
    elif stock.info['heldPercentInstitutions'] > .1:
        stock.info['institutionColor'] = 'bg-warning'
    else:
        stock.info['institutionColor'] = 'bg-success'

    if stock.info['trailingEps'] < 0:
        stock.info['epsColor'] = 'bg-success'
    else:
        stock.info['epsColor'] = 'bg-danger'

    
    if stock.info['fullTimeEmployees'] > 500:
        stock.info['employeesColor'] = 'bg-danger'
    elif stock.info['fullTimeEmployees'] > 100:
        stock.info['employeesColor'] = 'bg-warning'
    else:
        stock.info['employeesColor'] = 'bg-success'

    if stock.info['marketCap'] > 1e9:
        stock.info['marketCapColor'] = 'bg-danger'
    elif stock.info['marketCap'] > 1e8:
        stock.info['marketCapColor'] = 'bg-warning'
    else:
        stock.info['marketCapColor'] = 'bg-success'

    stock.info['marketCapDisplay'] = format_large_number(stock.info['marketCap'])




    # make a line chart of the daily stock price over last year
    hist = stock.history(period="1y")
    
    # we want to chart the closing price over last year in line chart
    # x-axis is the date should be displayed as string, but is a date time
    # y-axis is the closing price
    hist['Date'] = hist.index
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
    hist['Close'] = hist['Close'].astype(float)
    
    #plot width 800px height 500px
    plt.figure(figsize=(8,5))
    plt.plot(hist['Date'], hist['Close'])
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.title('Closing Price (Last 1 year)')
    plt.xticks(hist['Date'][::50], rotation=45)
    plt.tight_layout()
    plt.savefig('static/last_year.png')
    plt.close()



    # make a line plot of the 5 min 
    intraday = stock.history(period="1d", interval="5m")
    intraday['Date'] = intraday.index
    intraday['Date'] = intraday['Date'].dt.strftime('%H:%M')
    intraday['Close'] = intraday['Close'].astype(float)

    #plot
    plt.figure(figsize=(8,5))
    plt.plot(intraday['Date'], intraday['Close'])
    plt.xlabel('Time')
    plt.ylabel('Closing Price')
    plt.title('Price (5 min intervals)')
    plt.xticks(intraday['Date'][::50], rotation=45)
    plt.tight_layout()
    plt.savefig('static/intraday.png')
    plt.close()





    

    # Render the template with the financial data
    return render_template('financial_data.html', data=stock.info)

def format_large_number(num):
    if num >= 1_000_000_000:  # Greater than or equal to 1 billion
        formatted_num = f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:  # Greater than or equal to 1 million
        formatted_num = f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:  # Greater than or equal to 1 thousand
        formatted_num = f"{num / 1_000:.1f}K"
    else:
        formatted_num = str(num)
    return formatted_num

if __name__ == "__main__":
    app.run()
