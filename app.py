from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import yfinance as yf 

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

@app.route('/')
def index():
    return render_template('index.html') 

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

if __name__ == "__main__":
    app.run(debug=True)

