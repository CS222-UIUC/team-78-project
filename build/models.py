import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from statsmodels.tsa.api import ExponentialSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA


class TrainModel:
    """
    Class for training and making predictions with different time series models
    """

    def __init__(self, data, model_name, test_ratio=0.2):
        data.index = pd.to_datetime(data.index)
        self.date = np.array((data.index - data.index.min()).days).reshape(-1, 1)
        self.close = data["Close"].values.reshape(-1, 1)
        self.model_name = model_name
        self.test_ratio = test_ratio
        self.model = None

    def generate_split_data(self):
        """
        Splits the data into training and testing
        """
        X_train, X_test, y_train, y_test = train_test_split(
            self.date, self.close, test_size=self.test_ratio
        )
        return X_train, y_train, X_test, y_test

    def generate_model(self):
        """
        Fits model on training data based on model type
        """
        X_train, y_train, X_test, y_test = self.generate_split_data()

        if self.model_name == "linear_regression":
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            return self.model

        if self.model_name == "exponential_smoothing":
            self.model = ExponentialSmoothing(
                y_train.flatten(), trend="add", seasonal=None
            ).fit()
            return self.model

        if self.model_name == "holt":
            self.model = Holt(y_train.flatten()).fit()
            return self.model

        if self.model_name == "ARIMA":
            self.model = ARIMA(y_train.flatten(), order=(2, 2, 2)).fit()
            return self.model

        return "Invalid Model"

    def get_model_params(self):
        """
        Retrieves model parameters based on specified model
        """
        if self.model_name == "linear_regression" or isinstance(self.model, LinearRegression):
            return {
                "coefficients": self.model.coef_.tolist(),
                "intercept": self.model.intercept_.tolist(),
            }

        if self.model_name == "holt" or self.model_name == "exponential_smoothing" or isinstance(self.model, (ExponentialSmoothing, Holt)):
            return self.model.params

        if self.model_name == "ARIMA" or isinstance(self.model, ARIMA):
            return {"params": self.model.params.tolist(), "aic": self.model.aic}

        return None

    def make_predictions(self, num_preds):
        """
        Make future predictions using the trained model
        """
        if self.model_name == "linear_regression" or isinstance(self.model, LinearRegression):
            future_dates = np.arange(len(self.date), len(self.date) + num_preds).reshape(-1, 1)
            predictions = self.model.predict(future_dates).flatten().tolist()
            return {"future_predictions": predictions}

        if self.model_name == "holt" or self.model_name == "exponential_smoothing" or isinstance(self.model, (ExponentialSmoothing, Holt)):
            predictions = self.model.forecast(num_preds).tolist()
            return {"future_predictions": predictions}

        if self.model_name == "ARIMA" or isinstance(self.model, ARIMA):
            predictions = self.model.forecast(steps=num_preds).tolist()
            return {"future_predictions": predictions}

        return None


if __name__ == "__main__":
    apple_data = yf.Ticker("AAPL")
    apple_df = apple_data.history(period="1y")
    
    mod_train = TrainModel(apple_df, "holt")
    model = mod_train.generate_model()

    assert model != "Invalid Model", "Model has been generated"

    params = mod_train.get_model_params()
    print(params)
    assert params is not None, "Model Parameters are accessible"

    predictions = mod_train.make_predictions(5)
    print(predictions)
    assert predictions is not None, "Model Predictions are accessible"
