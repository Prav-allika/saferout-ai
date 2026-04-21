"""
Tire Failure Prediction Model
Uses Random Forest to predict tire failures
"""

import numpy as np  # numerical arrays
from sklearn.ensemble import RandomForestClassifier  # ML Tree model
from typing import Dict  # return values in dict format
import pickle  # save and load trained models
import os  # check if saved model file exists


class TireFailurePredictor:
    """Predicts tire failure probability using ML"""

    # Default path for persisting the trained model
    _MODEL_PATH = "models/tire_model.pkl"

    def __init__(self):
        self.model = None
        self.is_trained = False
        # Auto-load saved model so we never retrain from scratch on restart
        self.load_model(self._MODEL_PATH)

    # Strategy: Lazy training (train when needed, not immediately)
    def train_model(self, n_samples: int = 10000):
        """
        Train model on simulated tire failure data

        In production, you'd use real historical data.
        For this demo, we generate realistic training data.
        """
        print(f" Training tire failure model on {n_samples} samples...")

        # Generate training data
        X, y = self._generate_training_data(n_samples)

        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42
        )
        self.model.fit(X, y)  # Fit model on training data

        self.is_trained = True  # Model is trained

        # Calculate accuracy
        accuracy = self.model.score(X, y)  # get accuracy score
        print(f"Model trained! Training accuracy: {accuracy * 100:.1f}%")

        # Auto-save so the next startup skips retraining
        self.save_model(self._MODEL_PATH)

        return accuracy

    def _generate_training_data(self, n_samples: int):
        """
        Generate realistic tire failure training data using vectorized numpy ops.
        ~100x faster than a Python for-loop at 10,000 samples.

        Features:
        1. Current pressure (PSI)
        2. Temperature (°C)
        3. Tire age (months)
        4. Last rotation (months)
        5. Mileage (km)

        Label:
        0 = Safe
        1 = Will fail in next 48 hours
        """
        pressure = np.random.normal(32, 3, n_samples)
        temp = np.random.normal(42, 5, n_samples)
        age_months = np.random.randint(6, 36, n_samples)
        rotation_months = np.random.randint(0, 18, n_samples)
        mileage = np.random.randint(20000, 80000, n_samples)

        X = np.column_stack([pressure, temp, age_months, rotation_months, mileage])
        y = self._will_fail_vectorized(pressure, temp, age_months, rotation_months, mileage)

        return X, y

    def _will_fail_vectorized(self, pressure, temp, age, rotation, mileage):
        """
        Vectorized failure rules applied across all samples at once (numpy boolean ops).
        Equivalent logic to the original scalar _will_fail but runs on entire arrays.
        """
        fail = (
            ((pressure < 28) & (temp > 50))          # Critical pressure + high temp
            | (pressure < 26)                          # Very low pressure
            | ((age > 24) & (rotation > 12) & (mileage > 60000))  # Old + unmaintained
            | (temp > 60)                              # Overheating (friction/damage)
            | ((pressure < 29) & (age > 20))          # Low pressure + old tire
        )
        return fail.astype(int)

    def predict(self, tire_data: Dict) -> Dict:
        """
        Predict tire failure probability

        Args:
            tire_data: Dict with pressure, temp, age, etc.

        Returns:
            Dict with prediction results
        """
        if not self.is_trained:
            # Train on first use
            self.train_model()

        # Extract features
        features = [
            tire_data.get("pressure_psi", 32),
            tire_data.get("temperature_c", 40),
            tire_data.get("age_months", 12),
            tire_data.get("last_rotation_months", 3),
            tire_data.get("mileage_km", 40000),
        ]

        # Get prediction
        probability = self.model.predict_proba([features])[0][
            1
        ]  # get first element probability
        will_fail = probability > 0.7  # 70% threshold

        # Calculate time to failure (estimate)
        if will_fail:
            # Estimate based on pressure drop rate
            current_pressure = features[0]  # eg = 29.3 PSI
            critical_pressure = 28  # psi
            pressure_gap = current_pressure - critical_pressure  # 29.3 PSI - 28PSI

            # Assume 0.3 PSI drop per 5 seconds (from simulation)
            time_to_failure_hours = (pressure_gap / 0.3) * (5 / 3600)
            time_to_failure_hours = max(1, min(48, time_to_failure_hours))
        else:
            time_to_failure_hours = None

        return {
            "failure_probability": round(probability, 3),
            "will_fail": will_fail,
            "confidence": "HIGH" if abs(probability - 0.5) > 0.3 else "MEDIUM",
            "time_to_failure_hours": round(time_to_failure_hours, 1)
            if time_to_failure_hours
            else None,
            "recommendation": self._get_recommendation(probability),
        }

    def _get_recommendation(self, probability):
        """Get action recommendation based on probability"""
        if probability > 0.9:
            return "IMMEDIATE_SERVICE - Critical failure imminent"
        elif probability > 0.7:
            return "SERVICE_TODAY - High failure risk within 48 hours"
        elif probability > 0.5:
            return "SCHEDULE_SERVICE - Moderate risk, service within week"
        else:
            return "MONITOR - Low risk, continue monitoring"

    def save_model(self, filepath: str = "models/tire_model.pkl"):
        """Save trained model"""
        if self.is_trained:
            with open(filepath, "wb") as f:
                pickle.dump(self.model, f)  # DUMP MODEL TO DISK
            print(f"Model saved to {filepath}")

    def load_model(self, filepath: str = "models/tire_model.pkl"):
        """Load trained model"""
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                self.model = pickle.load(f)  # LOAD MODEL FROM DISK
            self.is_trained = True
            print(f"Model loaded from {filepath}")
        else:
            print(f" No saved model found, will train on first use")
