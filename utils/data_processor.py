"""
Data Processing Utility
Cleans, validates, and transforms sensor data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics


class DataProcessor:
    """Processes and validates sensor data"""

    @staticmethod
    def validate_sensor_data(sensor_data: Dict) -> Dict:
        """
        Validate sensor data and return validation result

        Returns:
            Dict with is_valid, errors, warnings
        """
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["vehicle_id", "timestamp", "tires", "engine"]
        for field in required_fields:
            if field not in sensor_data:
                errors.append(f"Missing required field: {field}")

        if errors:
            return {"is_valid": False, "errors": errors, "warnings": warnings}

        # Validate tire data
        tire_warnings = DataProcessor._validate_tires(sensor_data.get("tires", {}))
        warnings.extend(tire_warnings)

        # Validate engine data
        engine_warnings = DataProcessor._validate_engine(sensor_data.get("engine", {}))
        warnings.extend(engine_warnings)

        return {"is_valid": True, "errors": errors, "warnings": warnings}

    @staticmethod
    def _validate_tires(tires: Dict) -> List[str]:
        """Validate tire sensor data"""
        warnings = []

        for position, tire_data in tires.items():
            # Check pressure range
            pressure = tire_data.get("pressure_psi", 0)
            if pressure < 0 or pressure > 50:
                warnings.append(
                    f"Tire {position}: Pressure out of range ({pressure} PSI)"
                )

            # Check temperature range
            temp = tire_data.get("temperature_c", 0)
            if temp < 0 or temp > 100:
                warnings.append(f"Tire {position}: Temperature out of range ({temp}°C)")

        return warnings

    @staticmethod
    def _validate_engine(engine: Dict) -> List[str]:
        """Validate engine sensor data"""
        warnings = []

        # Check temperature range
        temp = engine.get("engine_temp_c", 0)
        if temp < 0 or temp > 150:
            warnings.append(f"Engine: Temperature out of range ({temp}°C)")

        # Check coolant
        coolant = engine.get("coolant_percent", 0)
        if coolant < 0 or coolant > 100:
            warnings.append(f"Engine: Coolant level invalid ({coolant}%)")

        return warnings

    @staticmethod
    def clean_sensor_data(sensor_data: Dict) -> Dict:
        """
        Clean sensor data by removing invalid values and applying constraints
        """
        cleaned = sensor_data.copy()

        # Clean tire data
        if "tires" in cleaned:
            for position, tire_data in cleaned["tires"].items():
                # Constrain pressure
                if "pressure_psi" in tire_data:
                    tire_data["pressure_psi"] = max(
                        0, min(50, tire_data["pressure_psi"])
                    )

                # Constrain temperature
                if "temperature_c" in tire_data:
                    tire_data["temperature_c"] = max(
                        0, min(100, tire_data["temperature_c"])
                    )

        # Clean engine data
        if "engine" in cleaned:
            engine = cleaned["engine"]

            if "engine_temp_c" in engine:
                engine["engine_temp_c"] = max(0, min(150, engine["engine_temp_c"]))

            if "coolant_percent" in engine:
                engine["coolant_percent"] = max(0, min(100, engine["coolant_percent"]))

        return cleaned

    @staticmethod
    def aggregate_sensor_history(sensor_history: List[Dict]) -> Dict:
        """
        Aggregate multiple sensor readings to get statistics

        Args:
            sensor_history: List of sensor data dictionaries

        Returns:
            Aggregated statistics
        """
        if not sensor_history:
            return {}

        # Extract tire pressures
        tire_pressures = {
            "front_left": [],
            "front_right": [],
            "rear_left": [],
            "rear_right": [],
        }

        engine_temps = []

        for data in sensor_history:
            # Collect tire data
            if "tires" in data:
                for position, tire in data["tires"].items():
                    if position in tire_pressures and "pressure_psi" in tire:
                        tire_pressures[position].append(tire["pressure_psi"])

            # Collect engine data
            if "engine" in data and "engine_temp_c" in data["engine"]:
                engine_temps.append(data["engine"]["engine_temp_c"])

        # Calculate statistics
        aggregated = {"tire_pressure_stats": {}, "engine_temp_stats": {}}

        # Tire statistics
        for position, pressures in tire_pressures.items():
            if pressures:
                aggregated["tire_pressure_stats"][position] = {
                    "mean": round(statistics.mean(pressures), 2),
                    "min": round(min(pressures), 2),
                    "max": round(max(pressures), 2),
                    "trend": "decreasing"
                    if pressures[-1] < pressures[0]
                    else "increasing"
                    if pressures[-1] > pressures[0]
                    else "stable",
                }

        # Engine statistics
        if engine_temps:
            aggregated["engine_temp_stats"] = {
                "mean": round(statistics.mean(engine_temps), 2),
                "min": round(min(engine_temps), 2),
                "max": round(max(engine_temps), 2),
                "trend": "increasing"
                if engine_temps[-1] > engine_temps[0]
                else "decreasing"
                if engine_temps[-1] < engine_temps[0]
                else "stable",
            }

        return aggregated

    @staticmethod
    def format_alert_for_sms(alert: Dict) -> str:
        """
        Format alert for SMS notification (160 char limit)
        """
        message = alert.get("message", "Alert")
        severity = alert.get("severity", "INFO")

        # Truncate and format
        if severity == "CRITICAL":
            prefix = "🚨 URGENT:"
        elif severity == "WARNING":
            prefix = "⚠️ WARNING:"
        else:
            prefix = "ℹ️ INFO:"

        max_length = 150 - len(prefix)
        truncated_message = message[:max_length]

        return f"{prefix} {truncated_message}"

    @staticmethod
    def extract_features_for_ml(
        sensor_data: Dict, position: str = "front_left"
    ) -> List[float]:
        """
        Extract features for ML model input

        Returns:
            List of features: [pressure, temp, age, rotation, mileage]
        """
        tire_data = sensor_data.get("tires", {}).get(position, {})
        metadata = sensor_data.get("metadata", {})

        features = [
            tire_data.get("pressure_psi", 32.0),
            tire_data.get("temperature_c", 40.0),
            tire_data.get("age_months", 12),
            tire_data.get("last_rotation_months", 3),
            metadata.get("mileage_km", 40000),
        ]

        return features
