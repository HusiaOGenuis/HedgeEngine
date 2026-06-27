import joblib
import numpy as np

class EVEngine:

    def __init__(self):
        self.model = joblib.load("models/ev_model.pkl")

    def evaluate_signal(self, signal):
        score = signal["signal_score"]

        ev = self.model.predict([[score]])[0]

        # Normalize to R units (approx scaling)
        ev_r = ev / 10000  

        return {
            "expected_win_prob": None,
            "expected_rr": None,
            "expected_value": ev_r
        }
