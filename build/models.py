import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

class TrainModel:
    """
    Class for training and making predictions with different time series models
    """

    def __init__(self, data, model_name, test_ratio=0.2):
        data.index = pd.to_datetime(data.index)
        self.date = np.array((data.index - data.index.min()).days).reshape(-1, 1)
        self.close = data["Close"].values.reshape(-1, 1)
        self.model_name = model_name.lower()
        self.test_ratio = test_ratio
        self.model = None

    def generate_split_data(self):
        return train_test_split(
            self.date, self.close, test_size=self.test_ratio, random_state=42
        )

    def generate_model(self):
        """
        Fits model on training data based on model type
        """
        x_train, x_test, y_train, y_test = self.generate_split_data()

        if self.model_name == "linear_regression":
            self.model = LinearRegression()
            self.model.fit(x_train, y_train)

        elif self.model_name == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(x_train, y_train.ravel())

        elif self.model_name == "k_neighbors":
            self.model = KNeighborsRegressor()
            self.model.fit(x_train, y_train.ravel())

        elif self.model_name == "svr":
            self.model = SVR(kernel="rbf", C=1.0, epsilon=0.1, gamma="scale")
            self.model.fit(x_train, y_train.ravel())

        else:
            raise ValueError(f"Invalid model name: {self.model_name}")

        return self.model

    def get_model_params(self):
        """
        Retrieves model parameters based on specified model
        """
        if isinstance(self.model, LinearRegression):
            return {
                "coefficients": [round(c, 4) for c in self.model.coef_.flatten()],
                "intercept": round(float(self.model.intercept_), 4),
            }

        if isinstance(self.model, RandomForestRegressor):
            return {
                "feature_importances": [round(f, 4) for f in self.model.feature_importances_]
            }

        if isinstance(self.model, KNeighborsRegressor):
            return {"n_neighbors": self.model.n_neighbors}

        if isinstance(self.model, SVR):
            return {
                "kernel": self.model.kernel,
                "C": self.model.C,
                "epsilon": self.model.epsilon,
                "gamma": self.model.gamma,
            }

        return None

    def make_predictions(self, num_preds):
        """
        Make future predictions using the trained model
        """
        sklearn_models = (
            LinearRegression,
            RandomForestRegressor,
            KNeighborsRegressor,
            SVR,
        )

        if isinstance(self.model, sklearn_models):
            future_dates = np.arange(
                len(self.date), len(self.date) + num_preds
            ).reshape(-1, 1)
            preds = self.model.predict(future_dates)
            return {"future_predictions": [round(float(p), 2) for p in preds]}

        return None

    def evaluate(self):
        if self.model is None:
            self.generate_model()

        x_train, x_test, y_train, y_test = self.generate_split_data()
        y_true = y_test.flatten()

        sklearn_models = (
            LinearRegression,
            RandomForestRegressor,
            KNeighborsRegressor,
            SVR,
        )

        if isinstance(self.model, sklearn_models):
            y_pred = self.model.predict(x_test).flatten()
        else:
            raise RuntimeError("Unknown model type in evaluate()")

        return {
            "r2":  r2_score(y_true, y_pred),
            "mse": mean_squared_error(y_true, y_pred),
            "mae": mean_absolute_error(y_true, y_pred),
        }


if __name__ == "__main__":
    apple_df = yf.Ticker("AAPL").history(period="1y")
    trainer = TrainModel(apple_df, "svr")
    model = trainer.generate_model()

    print("Params:", trainer.get_model_params())
    print("Preds:", trainer.make_predictions(5))
    print("Metrics:", trainer.evaluate())
