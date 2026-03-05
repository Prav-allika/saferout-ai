"""
Tire Failure Predictor Agent
Specialized agent that predicts tire failures using ML
"""

from typing import Dict
from models.tire_failure_model import TireFailurePredictor  # Random Forest classifier


class TirePredictorAgent:
    """Agent that predicts tire failures before they happen"""

    def __init__(self):
        self.predictor = TireFailurePredictor()  # The ML model object
        self.predictions_made = 0  # Counter (tracks usage)

    def analyze(
        self, tire_data: Dict, vehicle_metadata: Dict
    ) -> Dict:  # get tire data from sensors.py
        """
        Analyze tire and predict failure

        Args:
            tire_data: Current tire sensor data
            vehicle_metadata: Vehicle info (mileage, service history)

        Returns:
            Prediction with recommendations
        """
        self.predictions_made += 1  # track number of predictions made

        # Prepare data for ML model
        ml_input = {  # input data from 2 sources tire_data (from sensors.py), vehicle_metadata (from Vehicle class)
            "pressure_psi": tire_data["pressure_psi"],
            "temperature_c": tire_data["temperature_c"],
            "age_months": tire_data["age_months"],
            "last_rotation_months": tire_data["last_rotation_months"],
            "mileage_km": vehicle_metadata.get(
                "mileage_km", 40000
            ),  # "mileage_km" exists → use it, else default 40k
        }

        # Get ML prediction
        prediction = self.predictor.predict(ml_input)

        # Add context
        result = {
            "agent": "TirePredictorAgent",
            "tire_position": tire_data["position"],
            "current_status": tire_data["status"],
            "ml_prediction": prediction,
            "analysis": self._generate_analysis(tire_data, prediction),
        }

        return result

    def _generate_analysis(self, tire_data, prediction):
        """Generate human-readable analysis"""
        pressure = tire_data["pressure_psi"]
        temp = tire_data["temperature_c"]
        prob = prediction["failure_probability"]
        # Check will_fail:
        if prediction["will_fail"]:  # True
            if prediction["time_to_failure_hours"]:  # Check if time estimate exists:
                analysis = f"⚠️ HIGH RISK: {prob * 100:.0f}% probability of failure in next {prediction['time_to_failure_hours']:.0f} hours. "
            else:
                analysis = f"⚠️ HIGH RISK: {prob * 100:.0f}% probability of failure within 48 hours. "
            # Add pressure warning
            analysis += f"Current pressure ({pressure} PSI) is trending toward critical levels. "
            # Add temperature warning
            if temp > 45:
                analysis += (
                    f"Elevated temperature ({temp}°C) indicates increased friction. "
                )
        else:
            analysis = f" LOW RISK: {prob * 100:.0f}% failure probability. Tire operating normally. "

        return analysis
