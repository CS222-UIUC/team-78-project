from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import requests
import yfinance as yf 
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
import yfinance as yf
import matplotlib
import io
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np 
import models


app = Flask(__name__)
app.secret_key = 'supersecretkey' 

#  polygon.io has stock api for freee -> xayif58234@buides.com is email and password 
#  key: W1wT4puBL66ipVKe_BNHnV7JYGWMwEpX	 

NEWS_API_KEY = "W1wT4puBL66ipVKe_BNHnV7JYGWMwEpX"

@app.route('/')
def index():
    url = "https://api.polygon.io/v2/reference/news"
    params = {
        "ticker": "AAPL",  # default = aapl
        "limit": 5,        # num articles
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        news_data = response.json().get("results", [])
        for article in news_data:
            if 'published_utc' in article:
                article['formatted_date'] = datetime.strptime(
                    article['published_utc'], "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%B %d, %Y, %I:%M %p")
    else:
        news_data = [] 

    return render_template('index.html', articles=news_data)

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/stock_analysis')
def stock_analysis():
    return render_template('stock_analysis.html')

@app.route('/stock_comparison')
def stock_comparison():
    return render_template('stock_comparison.html')

@app.route('/account_settings')
def account_settings():
    return render_template('account_settings.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().upper()
    result = None

    if query:
        try:
            stock = yf.Ticker(query)
            info = stock.info

            result = {
                "symbol": query,
                "name": info.get("longName", "Unknown"),
                "price": info.get("regularMarketPrice", "N/A"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", "N/A"),
                "summary": info.get("longBusinessSummary", "No description available.")
            }
        except Exception as e:
            print(f"Error fetching stock info: {e}")

    return render_template("search_results.html", query=query, result=result)



@app.route('/favorite', methods=['POST'])
def favorite():
    symbol = request.form.get('symbol')

    if 'favorites' not in session:
        session['favorites'] = []

    if symbol and symbol not in session['favorites']:
        session['favorites'].append(symbol)
        session.modified = True

    return redirect(url_for('search', q=symbol))

@app.route('/favorites')
def favorites():
    favorite_symbols = session.get('favorites', [])
    favorite_data = []

    for symbol in favorite_symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            favorite_data.append({
                "symbol": symbol,
                "name": info.get("longName", "Unknown"),
                "price": info.get("regularMarketPrice", "N/A"),
                "currency": info.get("currency", "USD")
            })
        except Exception as e:
            print(f"Error fetching favorite stock info: {e}")

    return render_template('favorites.html', favorites=favorite_data)
    

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
    
    
@app.route('/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    try:
  
        # Fetch stock data
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
    
@app.route('/stock/<ticker>/graph', methods=['GET'])
def get_stock_graph(ticker):
    try:    
        # Get period from query parameters, default to 1 month
        period = request.args.get("period", "1mo")

        # Validate the period input
        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}
        if period not in valid_periods:
            return jsonify({"error": f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"}), 400
        
        stock = yf.Ticker(ticker)
        
        # Handle one day differently 
        if period == "1d":
            hist = stock.history(period = period, interval = "5m")
        else: 
            # Otherwise just use interval of one day
            hist = stock.history(period=period)
        # If there's not enough data, return an error
        if hist.empty:
            return jsonify({"error": f"No historical data found for {ticker} over period '{period}'."}), 404

        # Round Close prices
        hist["Close"] = hist["Close"].round(2)
        hist["Date"] = hist.index
      
    
        # Optionally resample for long periods
        long_periods = {"2y", "5y", "10y", "max"}
        if period in long_periods:
            hist = hist.resample("1W").mean()  # Weekly average

        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(hist["Date"], hist["Close"], linestyle='-', label=ticker.upper())

        # Format date axis
        
        if period in {"1d", "5d"}:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        elif period in {"1mo", "3mo", "6mo"}:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        elif period in {"1y", "2y"}:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price")
        ax.set_title(f"{ticker.upper()} Stock Price History ({period})")
        ax.grid(True)
        ax.legend()

        # Rotate and format ticks
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save to buffer
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        return send_file(img, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)

