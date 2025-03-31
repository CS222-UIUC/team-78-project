from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import yfinance as yf
import numpy as np 

""" 
This class is intended to take in the data and model information from the API call and upon training, 
return the appropriate jsonified outcome. 

"""
class train_model:
    def __init__(self, data, model, test_ratio = 0.2):
        self.data = data
        self.model = model
        self.test_ratio = test_split

    """
    Splits the provided time series data for model training and testing

    """

    def generate_split_data(self):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = self.test_ratio)

        self.X_train = X_train
        self.X_test = X_test 
        self.y_train = y_train 
        self.y_test = y_test

    """
    method for model training
    """

    def train_model(self):
        self.model.fit(self.X_train, self.y_train)
    
    """
    Return the model weights
    """

    def return_model_params(self):
        return self.model.get_params()



if __name__ == "__main__":
    pass