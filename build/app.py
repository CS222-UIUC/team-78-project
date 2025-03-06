from flask import Flask, jsonify, render_template, send_file
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt

app = Flask(__name__, template_folder='../public')


@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/stock/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1mo")  # Get last 1 month of data
        
        # Extract basic stock info
        current_price = info.get("currentPrice", "N/A")
        previous_close = info.get("previousClose", "N/A")
        market_cap = info.get("marketCap", "N/A")
        sector = info.get("sector", "N/A")
        currency = info.get("currency", "N/A")
        
        # Calculate day's change in percentage
        if current_price != "N/A" and previous_close != "N/A":
            change = round(((current_price - previous_close) / previous_close) * 100, 2)
        else:
            change = "N/A"

        # Convert historical data to JSON format
        hist_json = hist[['Close']].reset_index().to_dict(orient="records")

        return jsonify({
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "current_price": f"{current_price} {currency}" if current_price != "N/A" else "N/A",
            "change": f"{change}%" if change != "N/A" else "N/A",
            "market_cap": market_cap,
            "sector": sector,
            "historical_data": hist_json
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stock/<ticker>/graph', methods=['GET'])
def get_stock_graph(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo", interval = '1d')  # Get last 1 month of data

        if hist.empty:
            return jsonify({"error": "No data found for this stock"}), 404

        # Create a stock price graph
        plt.figure(figsize=(8, 4))
        plt.plot(hist.index, hist['Close'], label="Closing Price", color="blue")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.title(f"{ticker.upper()} Stock Price (Last 1 Month)")
        plt.legend()
        plt.grid(True)

    
        # Save the image and close the figure
        img_path = "stock_graph.png"
        plt.savefig(img_path)  
        plt.close()  # Close figure to prevent GUI issues
      

        return send_file(img_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)

