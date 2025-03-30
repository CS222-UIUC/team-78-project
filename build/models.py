from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from statsmodels.tsa.api import ExponentialSmoothing, Holt
import yfinance as yf
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

class train_model:
    def __init__(self, data, model_name, test_ratio=0.2):
        data.index = pd.to_datetime(data.index)
        
        self.date = np.array((data.index - data.index.min()).days).reshape(-1, 1)
        
        self.close = data["Close"].values.reshape(-1, 1)
        
        self.model_name = model_name
        self.test_ratio = test_ratio
        self.model = None

    """
    Splits the data into training and testing datasets
    """

    def generate_split_data(self):

        X_train, X_test, y_train, y_test = train_test_split(self.date, self.close, test_size=self.test_ratio)
        return X_train, y_train, X_test, y_test

    """
    Fits model on trianing data based on model type
    """

    def generate_model(self):
        X_train, y_train, X_test, y_test = self.generate_split_data()

        if self.model_name == "linear_regression":
            self.model = LinearRegression()


            self.model.fit(X_train, y_train)
            return self.model

        elif self.model_name == "exponential_smoothing":
            y_train_flat = y_train.flatten()

            self.model = ExponentialSmoothing(y_train_flat, trend="add", seasonal=None).fit()
            return self.model

        elif self.model_name == "holt":
            self.model = Holt(y_train.flatten()).fit()
            
            return self.model

        elif self.model_name == "ARIMA":
            
            self.model = ARIMA(y_train.flatten(), order=(2, 2, 2)).fit()  
                        
            return self.model
        
        return "Invalid Model"

    """
    Retrieved model paramerters

    """

    def get_model_params(self):
       
        if isinstance(self.model, LinearRegression):
            return {"coefficients": self.model.coef_.tolist(), "intercept": self.model.intercept_.tolist()}
        
        elif self.model_name == "holt" or self.model_name == "exponential_smoothing" or  isinstance(self.model, (ExponentialSmoothing, Holt)):
            return self.model.params

        elif self.name == "ARIMA" or isinstance(self.model, ARIMA):
            return {"params": self.model.params.tolist(), "aic": self.model.aic}

    """
    return predictions based on number of predictions inputted
    """

    def make_predictions(self, num_preds):
        """
        Make future predictions using the trained model.
        """
        if isinstance(self.model, LinearRegression):
            date_idx_end = len(self.date)
            date_idx_end_preds = len(self.date) + num_preds
            future_dates = np.arange(date_idx_end, date_idx_end_preds).reshape(-1, 1)
            
            predictions = self.model.predict(future_dates).flatten().tolist()
            return {"future_predictions": predictions}

        elif self.model_name == "holt" or self.model_name == "exponential_smoothing" or isinstance(self.model, (ExponentialSmoothing, Holt)):
            predictions = self.model.forecast(num_preds).tolist()

            
            return {"future_predictions": predictions}

        elif self.model_name == "ARIMA" or isinstance(self.model, ARIMA):
            predictions = self.model.forecast(steps=num_preds).tolist()
            return {"future_predictions": predictions}

        return {"Error": "Prediction not Permitted"}


if __name__ == "__main__":
    apple_data = yf.Ticker("AAPL")
    period = "1y"
    apple_df = apple_data.history(period=period)
    
    mod_train = train_model(apple_df, "holt")

    mod_train.generate_model()

    print(mod_train.get_model_params())
    print(mod_train.make_predictions(5))
