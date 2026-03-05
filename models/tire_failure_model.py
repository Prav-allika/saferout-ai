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

    def __init__(self):
        self.model = None  # no model yet
        self.is_trained = False  # not trained yet

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

        return accuracy

    def _generate_training_data(self, n_samples: int):
        """
        Generate realistic tire failure training data

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
        X = []
        y = []

        for _ in range(n_samples):
            # Generate random tire data
            pressure = np.random.normal(32, 3)  # Mean 32, std 3
            temp = np.random.normal(42, 5)  # Mean 42, std 5
            age_months = np.random.randint(6, 36)
            rotation_months = np.random.randint(0, 18)
            mileage = np.random.randint(20000, 80000)

            # Determine if tire will fail (based on realistic rules)
            failure = self._will_fail(
                pressure, temp, age_months, rotation_months, mileage
            )

            X.append([pressure, temp, age_months, rotation_months, mileage])
            y.append(1 if failure else 0)

        return np.array(X), np.array(y)

    def _will_fail(self, pressure, temp, age, rotation, mileage):
        """
        Realistic tire failure rules
        (Based on research on tire failures)
        """
        # Critical pressure + high temp
        if pressure < 28 and temp > 50:
            return True

        # Very low pressure
        if pressure < 26:
            return True

        # Old tire + not rotated + high mileage
        if age > 24 and rotation > 12 and mileage > 60000:
            return True

        # High temp (friction/damage)
        if temp > 60:
            return True

        # Moderately low pressure + old tire
        if pressure < 29 and age > 20:
            return True

        return False

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
