from flask import Flask, jsonify, request
import yfinance as yf
from flask_cors import CORS
from flask import Flask, jsonify, render_template
import yfinance as yf
import numpy as np 
import models

app = Flask(__name__)
CORS(app)  # allow cross-origin requests from frontend

@app.route('/api/search')
def search_stock():
    query = request.args.get('query', '').upper().strip()
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    try:
        stock = yf.Ticker(query)
        info = stock.info
        result = {
            'symbol': info.get('symbol', query),
            'name': info.get('shortName', 'Unknown'),
            'price': info.get('regularMarketPrice', 'N/A'),
        }
        return jsonify({'stocks': [result]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return 'API is running'
    return render_template('public/index.html') 


"""
- Route below fetches the stock history based on the ticker and period, which is set to 1 year by default
"""

@app.route('/stock/<stock_ticker>/<period>', methods = ['GET'])
def search_stock_data(stock_ticker, period = '1y'):
    stock = yf.Ticker(stock_ticker)
    stock_history = stock.history(period = period)

    if not hist.empty:
        return jsonify(hist['Close'].to_dict())

    return {"Ticker error: Ticker not found"}


@app.route('/stock_info/<stock_ticker>/', method = ['GET'])
def get_other_stock_data():
    stock = yf.Ticker(ticker)

    stock_info = stock.info 

    """
    This will return relevant stock information in json format
    """
    return None

"""
- App route will expect the model type, stock ticker, and period in time.
- This route will return the results of a specific model
"""
@app.route('/predict/<model>/<ticker>/<period>')
def predict_future_stock_price(model, ticker, period = "1y"):
    stock = yf.Ticker(ticker)

    stock_history = stock.history(period = period)  

    prices_data_y = stock_history['Close'].values
    values = len(prices_data_y)
    time_days_X = np.arange(values).reshape(-1, 1)

    

    """
    The prices data and X (time) will be sent to our models python file and the model results will be returned
    """


if __name__ == "__main__":
    app.run(debug=True)
