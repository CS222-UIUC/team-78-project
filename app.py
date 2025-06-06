from flask import Flask, jsonify, render_template, request, redirect, url_for, session, send_file, redirect, flash
import requests
import yfinance as yf 
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'build')))
from models import TrainModel
import plotly.express as px
import plotly.io as pio
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import numpy as np


app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route("/logout")
def logout():
    session.clear()  
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        

        user = conn.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
       
        if user is None: 
            flash("Invalid username or password.", "error")
            return redirect("/login")

        stored_password = user["password"].decode("utf-8") if isinstance(user["password"], bytes) else user["password"]
        if check_password_hash(stored_password, password):
            session["user_id"] = user["id"]
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
    metrics = None
    plot_html = None

    if request.method == 'POST':
        ticker_query = request.form.get('q').upper() 
        time_period = request.form.get('time_period')  
        model_type = request.form.get('model_type') 
        prediction_horizon = int(request.form.get('prediction_horizon'))  

        if ticker_query and time_period and model_type and prediction_horizon:
            stock_data = yf.Ticker(ticker_query).history(period = time_period)
            stock_data['Close'].dropna(inplace=True)
            train_mod = TrainModel(stock_data, model_type)
            train_mod.generate_model()
            predictions = train_mod.make_predictions(prediction_horizon)
            metrics = train_mod.evaluate()
            
            x_all_dates = train_mod.dates
            y_all_close = np.array(train_mod.close.flatten()).round(2)
            
            # Model fitted predictions over training period
            fitted_preds = train_mod.model.predict(train_mod.date).flatten().round(2)
           
            # Future dates
            last_date = x_all_dates[-1]
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=prediction_horizon)

            future_preds = np.array(predictions["future_predictions"]).round(2)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=x_all_dates, y=y_all_close,
                mode="lines", name="Historical Close"
            ))

            fig.add_trace(go.Scatter(
                x=x_all_dates, y=fitted_preds,
                mode="lines", name="Model Fit"
            ))

            fig.add_trace(go.Scatter(
                x=future_dates, y=future_preds,
                mode="lines", name="Predictions"
            ))

            fig.update_layout(
                title=f"{ticker_query.upper()} Stock Price Prediction",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                template="plotly_white",
                height=500,
            )

            plot_html = pio.to_html(fig, full_html=False)

        return render_template('predict.html', 
            ticker_query=ticker_query, 
            time_period=time_period, 
            model_type=model_type, 
            prediction_horizon=prediction_horizon, 
            predictions=predictions,
            metrics=metrics,
            model_params=train_mod.get_model_params(),
            plot_html=plot_html, 
        )
    else:
        return render_template('predict.html', 
            ticker_query=ticker_query, 
            time_period=time_period, 
            model_type=model_type, 
            prediction_horizon=prediction_horizon, 
            predictions=predictions,
            metrics=metrics,
            plot_html=plot_html, 
        )



@app.route('/analysis')
def stock_analysis():
    return render_template('stock_analysis.html')

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
    symbol = request.form.get('symbol', '').upper()
    if not symbol:
        return redirect(url_for('index'))

    # user must be logged in
    if 'user_id' not in session:
        flash("Please log in to save favourites.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute(
        'INSERT OR IGNORE INTO favorites (user_id, symbol) VALUES (?, ?)',
        (user_id, symbol)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('search', q=symbol))


@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        flash("Log in to see your favourites.", "error")
        return redirect(url_for('login'))

    conn = get_db_connection()
    rows = conn.execute(
        'SELECT symbol FROM favorites WHERE user_id = ?',
        (session['user_id'],)
    ).fetchall()
    conn.close()

    symbols = [row['symbol'] for row in rows]
    favorite_data = []
    for sym in symbols:
        try:
            info = yf.Ticker(sym).info
            favorite_data.append({
                "symbol": sym,
                "name": info.get("longName", "Unknown"),
                "price": info.get("regularMarketPrice", "N/A"),
                "currency": info.get("currency", "USD"),
            })
        except Exception as e:
            app.logger.warning(f"Ticker fetch failed for {sym}: {e}")

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


@app.route('/stock/<ticker>/history_data', methods=['GET'])
def get_stock_history_data(ticker):
    try:
        period = request.args.get("period", "1mo")
        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"}
        if period not in valid_periods:
            return jsonify({"error": f"Invalid period '{period}'."}), 400

        stock = yf.Ticker(ticker)
        if period == "1d":
            historical_data = stock.history(period=period, interval="5m")
        else:
            historical_data = stock.history(period=period)

        if historical_data.empty:
            return jsonify({"error": f"No historical data found for {ticker} over period '{period}'."}), 404

        historical_data["Close"] = historical_data["Close"].round(2)
        historical_data["Date"] = historical_data.index
        historical_data["Close"].replace({np.nan: None}, inplace=True)
        if period == "1d":
            # Include time for intraday data
            dates = historical_data["Date"].dt.strftime("%Y-%m-%d %H:%M").tolist()
        else:
            dates = historical_data["Date"].dt.strftime("%Y-%m-%d").tolist()

        closes = historical_data["Close"].tolist()
        history = [{"date": d, "close": c} for d, c in zip(dates, closes)]

        return jsonify({"history": history})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/<ticker>/percent_change', methods=['GET'])
def get_percent_change(ticker):
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
      
        # Optionally resample for long periods
        long_periods = {"2y", "5y", "10y", "max"}
        if period in long_periods:
            historical_data = historical_data.resample("1W").mean()  # Weekly average
            
        # Process data 
        historical_data["Date"] = historical_data.index
        historical_data["Close"] = historical_data["Close"].round(2)
        historical_data["Percent Change"] = ((historical_data["Close"] / historical_data["Close"].iloc[0]) - 1) * 100
        historical_data["Percent Change"] = historical_data["Percent Change"].round(2)

        # Return only date, close, and percent change
        response_data = historical_data[["Date", "Close", "Percent Change"]].reset_index(drop=True)
        response_data["Date"] = response_data["Date"].dt.strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(response_data.to_dict(orient="records"))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_volume(volume):
    """Convert volume to a human-readable format."""
    if volume is None:
        return "N/A"
    elif volume >= 1e12:
        return f"{volume / 1e12:.2f}T"
    elif volume >= 1e9:
        return f"{volume / 1e9:.2f}B"
    elif volume >= 1e6:
        return f"{volume / 1e6:.2f}M"
    else:
        return f"{volume:.2f}"

@app.route('/stock/<ticker>/volume', methods=['GET'])
def get_volume(ticker):
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
            historical_data = stock.history(period=period, interval="5m")
        else:
            historical_data = stock.history(period=period)

        if historical_data.empty:
            return jsonify({"error": f"No volume data found for {ticker} over period '{period}'."}), 404

        # Optionally resample for long periods
        long_periods = {"2y", "5y", "10y", "max"}
        if period in long_periods:
            historical_data = historical_data.resample("1W").mean()

        # Process data 
        historical_data["Date"] = historical_data.index
        response_data = historical_data[["Date", "Volume"]].reset_index(drop=True)
        response_data["Date"] = response_data["Date"].dt.strftime('%Y-%m-%d %H:%M:%S')
        response_data["Volume"] = response_data["Volume"].apply(format_volume)

        return jsonify(response_data.to_dict(orient="records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(debug=True, port = 8000)

