from flask import Flask, request, jsonify, render_template, send_file
import yfinance as yf
import matplotlib
import io
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

app = Flask(__name__, template_folder='../public')

# Home page
@app.route('/')
def index():
    return render_template('index.html') 


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
        # Get period from query parameters, default to 1 month
        period = request.args.get("period", "1mo")

        # Validate the period input
        valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
        if period not in valid_periods:
            return jsonify({"error": f"Invalid period '{period}'. Valid options: {', '.join(valid_periods)}"}), 400

        # Fetch stock data
        stock = yf.Ticker(ticker)
        info = stock.info

        # Ensure stock data is available
        if not info or "currentPrice" not in info:
            return jsonify({"error": f"No data found for ticker '{ticker}'"}), 404

        hist = stock.history(period=period)
        if hist.empty:
            return jsonify({"error": f"No historical data available for ticker '{ticker}' and period '{period}'"}), 404

        # Extract relevant stock info
        current_price = round(info.get("currentPrice", 0), 2)
        market_cap = format_market_cap(info.get("marketCap"))
        sector = info.get("sector", "N/A")
        currency = info.get("currency", "N/A")

        # Convert historical data to JSON format
        hist_json = hist[['Close']].reset_index()
        hist_json["Date"] = hist_json["Date"].dt.strftime('%m-%d-%Y')  # Convert timestamp
        hist_json["Close"] = hist_json["Close"].round(2)  # Round Close prices
        hist_json = hist_json.to_dict(orient="records")

        return jsonify({
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "current_price": f"{current_price} {currency}" if current_price != "N/A" else "N/A",
            "market_cap": market_cap,
            "sector": sector,
            "historical_data": hist_json
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/stock/<ticker>/graph', methods=['GET'])
def get_stock_graph(ticker):
    try:
        period = request.args.get("period", "1mo")  # Default 1 month
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        # Round Close prices and format dates
        hist["Close"] = hist["Close"].round(2)
        hist["Date"] = hist.index.strftime('%m-%d-%Y')

        # Generate plot
        plt.figure(figsize=(12, 9))
        plt.plot(hist["Date"], hist["Close"], marker='o', linestyle='-')
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.title(f"Stock Price History: {ticker.upper()} ({period})")
        plt.xticks(rotation=45)
        plt.grid()

        # Save plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        return send_file(img, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)

