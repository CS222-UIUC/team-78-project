import pytest
import yfinance as yf 
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../build')))

from models import TrainModel


def test_models():
    apple_df = yf.Ticker("AAPL").history(period="1y")
    
    trainer = TrainModel(apple_df, "random_forest")
    
    model = trainer.generate_model()

    assert model != "Invalid Model", "Model has been generated"

    params = trainer.get_model_params()

    assert params is not None, "Model Parameters are accessible"

    predictions = trainer.make_predictions(5)

    assert predictions is not None, "Model Predictions are accessible"

    metrics = trainer.evaluate()

    assert metrics is not None, "Model Metrics are accessible"


if __name__ == "__main__":
    test_models()