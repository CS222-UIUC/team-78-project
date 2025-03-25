from flask import Flask, jsonify, request
import yfinance as yf
from flask_cors import CORS

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

if __name__ == "__main__":
    app.run(debug=True)
