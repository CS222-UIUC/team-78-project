from flask import Flask, jsonify, render_template, request, redirect, url_for, session, send_file, redirect, flash
import requests
import yfinance as yf 
from datetime import datetime
import matplotlib
import io
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np 
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'build')))
from models import TrainModel
import plotly.express as px
import plotly.io as pio
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # CONNECT STUFF IS WORK IN PROGRESS --> still working out some stuff, this is groundwork for future features
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        

        user = conn.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
       
        if user is None: 
            flash("Invalid username or password.", "error")
            return redirect("/login")

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session["user_id"] = user[0]
            session["username"] = username
            return redirect("/")
        else:
            return "Invalid credentials. Please try again.", 401

    return render_template("login.html")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]
    conn = get_db_connection()
    try:
        hashed_password = generate_password_hash(password)
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        flash(f"Account created. Welcome, {username}!", "success")
    except sqlite3.IntegrityError:
        flash("Username already exists. Please choose a different username.", "error")
    finally:
        conn.close()
    return redirect(url_for("account_settings"))


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

@app.route('/predict', methods=['GET', 'POST'])
def models():
    ticker_query = ''
    time_period = '1d'  
    model_type = 'linear_regression'  
    prediction_horizon = 1  
    predictions = None
    if request.method == 'POST':
        ticker_query = request.form.get('q').upper() 
        time_period = request.form.get('time_period')  
        model_type = request.form.get('model_type') 
        prediction_horizon = int(request.form.get('prediction_horizon'))  

        if ticker_query and time_period and model_type and prediction_horizon:
            stock_data = yf.Ticker(ticker_query).history(period = time_period)
            stock_data['Close'].dropna(inplace=True)
            print(stock_data)
            train_mod = TrainModel(stock_data, model_type)
            train_mod.generate_model()
            predictions = train_mod.make_predictions(prediction_horizon)



    return render_template('predict.html', 
                               ticker_query=ticker_query, 
                               time_period=time_period, 
                               model_type=model_type, 
                               prediction_horizon=prediction_horizon, predictions = predictions)
    

@app.route('/analysis')
def stock_analysis():
    return render_template('analysis.html')

@app.route('/comparison')
def stock_comparison():
    return render_template('comparison.html')

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
            historical_data = stock.history(period = period, interval = "5m")
        else: 
            # Otherwise just use interval of one day
            historical_data = stock.history(period=period)
        # If there's not enough data, return an error
        if historical_data.empty:
            return jsonify({"error": f"No historical data found for {ticker} over period '{period}'."}), 404

        # Round Close prices
        historical_data["Close"] = historical_data["Close"].round(2)
        historical_data["Date"] = historical_data.index
      
    
        # Optionally resample for long periods
        long_periods = {"2y", "5y", "10y", "max"}
        if period in long_periods:
            historical_data = historical_data.resample("1W").mean()  # Weekly average
        # Interactive Plotly chart
        fig = px.line(
            historical_data,
            x="Date",
            y="Close",
            title=f"{ticker.upper()} Stock Price History ({period})",
            labels={"x": "Date", "Close": "Close Price"},
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Close Price",
            hovermode="x unified",
            template="plotly_white"
        )

        # Convert to HTML div
        graph_html = pio.to_html(fig, full_html=False)

        return jsonify({"graph_html": graph_html})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(debug=True)

