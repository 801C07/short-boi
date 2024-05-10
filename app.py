import sys
import yfinance as yf
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/ticker/<symbol>')
def get_financial_data(symbol):
    stock = yf.Ticker(symbol)

    # heldPercentInsiders and heldPercentInstitutions are in scientific notation, they should be converted to strings and displayed as percentages
    stock.info['heldPercentInsiders'] = "{:.2%}".format(stock.info['heldPercentInsiders'])
    stock.info['heldPercentInstitutions'] = "{:.2%}".format(stock.info['heldPercentInstitutions'])
    
    

    # Render the template with the financial data
    return render_template('financial_data.html', data=stock.info)

if __name__ == "__main__":
    app.run()
