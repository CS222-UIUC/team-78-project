import pytest
import yfinance as yf 
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../build')))

from models import TrainModel

def test_models():
    apple_data = yf.Ticker("AAPL")
    period = "1y"
    apple_df = apple_data.history(period=period)
    
    mod_train = TrainModel(apple_df, "holt")

    model = mod_train.generate_model()

    assert model != "Invalid Model", "Model has been generated"

    params = mod_train.get_model_params()

    assert params is not None, "Model Parameters are accessible"

    predictions = mod_train.make_predictions(5)

    assert predictions is not None, "Model Predictions are accessible"




if __name__ == "__main__":
    test_models()