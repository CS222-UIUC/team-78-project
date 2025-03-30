from flask import Flask, request, jsonify, render_template, send_file
import yfinance as yf
import matplotlib
import io
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np 
import models
import plotly.graph_objs as go
import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot

app = Flask(__name__, template_folder='../public')

# Home page
@app.route('/')
def index():
    return render_template('index.html') 


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


@app.route('/stock_info/<stock_ticker>/', methods = ['GET'])
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





def format_market_cap(market_cap):
    """Convert market cap to a human-readable format."""
    if market_cap is None:
        return "N/A"
    elif market_cap >= 1e12:
        return f"{market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"{market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"{market_cap / 1e6:.2f}M"
    else:
        return f"{market_cap:.2f}"
    
    
@app.route('/stock/<ticker>/info', methods=['GET'])
def get_stock_info(ticker):
    try:
  
        # Fetch stock info
        stock = yf.Ticker(ticker)
        info = stock.info

        # Ensure stock data is available
        if not info or "currentPrice" not in info:
            return jsonify({"error": f"No data found for ticker '{ticker}'"}), 404

        # Extract relevant stock info
        current_price = round(info.get("currentPrice", 0), 2)
        market_cap = format_market_cap(info.get("marketCap"))
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        currency = info.get("currency", "N/A")

        return jsonify({
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "current_price": f"{current_price} {currency}" if current_price != "N/A" else "N/A",
            "market_cap": market_cap,
            "sector": sector,
            "industry": industry,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Route to serve a stock price graph for a given ticker
@app.route('/stock/<ticker>/graph', methods=['GET'])
def get_stock_graph(ticker):
    try:
        # Get time period from the request parameters, default 1 month
        user_period = request.args.get("period", "1mo")

        # Valid periods allowed by the yfinance API
        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}

        # Invalid request period
        if user_period not in valid_periods:
            return jsonify({"error": f"Invalid period '{user_period}'."}), 400

    
        stock = yf.Ticker(ticker)

        # Fetch historical data
        hist = stock.history(period=user_period)

        # If no data is returned
        if hist.empty:
            return jsonify({"error": "No historical data found."}), 404

        # Round 'Close' prices to two decimal places
        hist["Close"] = hist["Close"].round(2)

        # Add a 'Date' column 
        hist["Date"] = hist.index

        # Create a line chart trace with markers for the 'Close' prices
        trace = go.Scatter(
            x=hist["Date"], 
            y=hist["Close"], 
            mode="lines+markers", 
            name="Close"
        )

        # Define the layout of the plot including title, axis labels, and date range selector
        layout = go.Layout(
            title=f"{ticker.upper()} Close Price ({user_period})",
            xaxis=dict(
                title="Date",
                rangeselector=dict(
                    buttons=[
                        dict(count=7, label="1w", step="day", stepmode="backward"),
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=3, label="3m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ]
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis=dict(title="Close Price ($)"),
            template="plotly_white"
        )

        # Create figure
        fig = go.Figure(data=[trace], layout=layout)

        # Convert the figure to HTML (without full HTML document) to embed in a webpage
        graph_html = pio.to_html(fig, full_html=False)

        return graph_html

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

