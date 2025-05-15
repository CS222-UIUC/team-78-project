# Stock Price Forecasting Dashboard
## CS 222 Project Group 78
#### Group Members: Advay Kadam, Michael Ling, Jeslin Paulraj, Soham Phargade
#### Mentor: Simran Malhotra
<!-- Command + Shift + V in VSCode for Preview -->


### Team Members & Roles
Our team is divided into frontend and backend roles:

- **Frontend Team**:
  - **Jeslin** - UI development, frontend styling, API integration.
  - **Soham** - UI development, API integration, assisting backend.

- **Backend Team**:
  - **Advay** - Data visualization, backend implementation, machine learning.
  - **Michael** - Data cleaning, backend implementation, machine learning.

## Introduction
### What is the Stock Price Forecasting Dashboard?
Stock pricing and prediction dates back centuries, but now with modern statistical modeling and machine learning techniques, this concept allows users to mathematically predict market performance. Hence, our stock price forecasting dashboard allows users to select a stock of their choice and train an ML model of their choice – displaying the results for the model visually and on different time scales. 

### Key Features
- View both the historical and latest stock prices and data (Past day, Last 5 days, 1 month, etc.).
- View summary information for selected stocks.
- Train ML models on past data to forecast future prices.
- Specify forecast intervals.
- Compare key performance indicators (KPIs) of different models.
- Compare various stocks side by side.

Please review the project proposal for more details.

---

## Technical Architecture
### Backend
We used Python and Flask and the following libraries:
- **Yahoo Finance (`yfinance`)** for retrieving the stock data.
- **NumPy, Pandas, Scikit-Learn** for processing and handling data.
- **Statsmodels** for statistical modeling.
- **Flask API** for serving the data to the frontend.
- **SQLite** for database management.

Stock Prediction Models we use using Scikit-Learn:
- **Linear Regression** 
- **Random Forest Regressor** 
- **k-Nearest Neighbors Regressor** 
- **Support Vector Regression** 
---

### Frontend
We used **React.js, HTML, and Tailwind CSS** along with
- **React Components** for modular UI development.
- **Tailwind CSS** for flexible styling.
- **React Testing Library & Cypress** for frontend testing.
---

### Continuous Integration/Deployment (CI/CD) & GitHub Workflow
- **GitHub Actions** for testing and enforcing style/lint checks (`ESLint` for JavaScript, `Pylint` for Python).
- **GitHub Workflow**:
  - Main branch for stable code.
  - Individual branches for team members.
  - Code is developed, tested, and merged into `main` after passing integration tests.

---

## Environment Setup
### Initial Virtual Environment Installation
Go to the source directory and run: ``` python3 -m venv ./venv

Starting The Virtual Environment

for macOS/Linux: source venv/bin/activate  
for Windows: venv\Scripts\activate  

Development + Package Updates:

To enable package updates, run:
pip install pipreqs

To update packages, execute:
pipreqs . --force

To install dependencies:
pip install -r requirements.txt

Project Instructions

Fetch Stock Data:
python src/data_fetch.py <stock_symbol>

Train a Model:
python src/model_train.py <stock_symbol> <model_name>

Get Forecasted Prices:
python src/predict.py <stock_symbol> <model_name> <time_interval>

Save and Retrieve Favorite Stocks:

python src/user_preferences.py save <stock_symbol>
python src/user_preferences.py retrieve
