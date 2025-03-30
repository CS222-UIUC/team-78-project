from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/favorites')
def favorites():
    return render_template('favorites.html')

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

if __name__ == "__main__":
    app.run(debug=True)

