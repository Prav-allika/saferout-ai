"""
Realistic IoT sensor simulation
NO HARDWARE NEEDED!
"""

import random
from datetime import datetime
from typing import Dict
from config.settings import settings


class TireSensor:
    """Simulates TPMS (Tire Pressure Monitoring System)"""

    def __init__(self, vehicle_id: str, tire_position: str):
        self.vehicle_id = vehicle_id
        self.tire_position = tire_position

        # Initialize with normal values, * - for random.uniform() takes 2 arguments
        self.pressure = random.uniform(
            *settings.TIRE_PRESSURE_NORMAL
        )  # Returns value between 32 and 35
        self.temperature = random.uniform(*settings.TIRE_TEMP_NORMAL)

        # Tire metadata
        self.age_months = random.randint(6, 24)
        self.last_rotation_months = random.randint(0, 6)

        # Failure simulation
        self.is_failing = False
        self.failure_rate = 0.0  # How fast it's failing

    def simulate_failure(
        self, rate: float = 0.5
    ):  ####how its checking and saying failing is true?
        """Start simulating gradual failure"""
        self.is_failing = True  ## Now: is_failing=True, failure_rate=0.3
        self.failure_rate = rate  # (gradual drop over time)

    def update(self) -> Dict:
        """Update sensor reading (call every 5 seconds)"""

        if self.is_failing:
            # Simulate gradual pressure drop
            self.pressure -= self.failure_rate
            # Friction causes temperature increase
            self.temperature += random.uniform(0, 0.3)
        else:
            # Normal random fluctuation
            self.pressure += random.uniform(-0.1, 0.1)
            self.temperature += random.uniform(-0.2, 0.2)

        # Keep in realistic bounds
        self.pressure = max(0, self.pressure)
        self.temperature = max(20, min(70, self.temperature))

        return {
            "vehicle_id": self.vehicle_id,
            "position": self.tire_position,
            "pressure_psi": round(self.pressure, 1),
            "temperature_c": round(self.temperature, 1),
            "age_months": self.age_months,
            "last_rotation_months": self.last_rotation_months,
            "timestamp": datetime.now().isoformat(),
            "status": self._get_status(),
        }  # This is called every 5 seconds!

    def _get_status(self) -> str:  # to determine the tire status
        """Determine tire status"""
        if self.pressure < 28:
            return "CRITICAL"
        elif self.pressure < 30:
            return "WARNING"
        else:
            return "OK"


class EngineSensor:
    """Simulates OBD-II engine diagnostics"""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.temperature = random.uniform(
            *settings.ENGINE_TEMP_NORMAL
        )  ## Random 85-95°C (normal)
        self.coolant_level = 100  # full
        self.is_overheating = False

    def simulate_overheat(self):
        """Start simulating engine overheat"""
        self.is_overheating = True

    def update(self) -> Dict:
        """Update engine readings"""

        if self.is_overheating:
            self.temperature += random.uniform(0.5, 2.0)
            self.coolant_level -= random.uniform(0.5, 1.5)
        else:
            self.temperature += random.uniform(-1, 1)

        # Bounds
        self.temperature = max(60, min(120, self.temperature))
        self.coolant_level = max(0, min(100, self.coolant_level))
        # Oil pressure and RPM fluctuate constantly based on driving
        return {
            "vehicle_id": self.vehicle_id,
            "engine_temp_c": round(self.temperature, 1),
            "coolant_percent": round(self.coolant_level, 1),
            "oil_pressure_psi": round(
                random.uniform(35, 65), 1
            ),  # Oil pressure varies with engine speed
            "rpm": random.randint(1500, 3000),  # RPM changes with acceleration
            "timestamp": datetime.now().isoformat(),
            "status": "CRITICAL"
            if self.temperature > 110
            else "WARNING"
            if self.temperature > 100
            else "OK",
        }


class Vehicle:
    """Complete vehicle with all sensors"""

    def __init__(self, vehicle_id: str, simulation_mode: str = "normal"):
        self.vehicle_id = vehicle_id
        self.simulation_mode = simulation_mode

        # Create 4 tire sensors
        self.tires = {
            "front_left": TireSensor(vehicle_id, "front_left"),
            "front_right": TireSensor(vehicle_id, "front_right"),
            "rear_left": TireSensor(vehicle_id, "rear_left"),
            "rear_right": TireSensor(vehicle_id, "rear_right"),
        }

        # Create engine sensor
        self.engine = EngineSensor(vehicle_id)

        # Activate simulation mode
        if simulation_mode == "tire_failure":
            self.tires["front_left"].simulate_failure(0.3)
        elif simulation_mode == "engine_overheat":
            self.engine.simulate_overheat()

        # Vehicle metadata
        self.mileage = random.randint(20000, 60000)
        self.last_service_months = random.randint(1, 6)

    def get_sensor_data(self) -> Dict:
        """Get all sensor data"""
        return {
            "vehicle_id": self.vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "tires": {name: tire.update() for name, tire in self.tires.items()},
            "engine": self.engine.update(),
            "metadata": {
                "mileage_km": self.mileage,
                "last_service_months": self.last_service_months,
                "simulation_mode": self.simulation_mode,
            },
        }
