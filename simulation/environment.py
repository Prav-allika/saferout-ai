"""
Environment Simulation - Weather & Roads
Simulates external conditions that affect vehicle safety
"""

import random  # generate realistic weather variations
from datetime import datetime  # timestamp weather data
from typing import Dict, List


class WeatherSimulator:
    """Simulates weather API responses"""

    # all possible weather conditions
    CONDITIONS = ["clear", "cloudy", "rain", "heavy_rain", "fog", "storm"]

    # Weather patterns by month (for realism)
    MONSOON_MONTHS = [6, 7, 8, 9]  # June-September in India

    @staticmethod
    def get_weather(lat: float = 17.3850, lon: float = 78.4867) -> Dict:
        """
        Simulate weather API (like OpenWeatherMap)

        Args:
            lat: Latitude (default: Hyderabad)
            lon: Longitude (default: Hyderabad)

        Returns:
            Weather data dictionary
        """
        current_month = datetime.now().month  # Get current month to determine monsoon
        is_monsoon = (
            current_month in WeatherSimulator.MONSOON_MONTHS
        )  # Check if current month is in monsoon months

        # Bias conditions based on season
        if is_monsoon:
            # Monsoon: More rain/storms, less clear weather
            condition = random.choices(  # Picks a random number between 0–100
                WeatherSimulator.CONDITIONS,
                weights=[10, 20, 30, 20, 10, 10],  # 30% rain, 20% heavy_rain
                k=1,
            )[0]  # eg: output: "Rainy"
        else:
            # Non-monsoon: Mostly clear, occasional rain
            condition = random.choices(
                WeatherSimulator.CONDITIONS,
                weights=[40, 30, 15, 5, 5, 5],  # 40% clear, 15% rain
                k=1,
            )[0]  # eg: output: "Sunny"

        # Temperature varies by season
        if is_monsoon:
            temp = random.randint(25, 32)  # Cooler during monsoon
        else:
            temp = random.randint(30, 38)

        # Rain probability for next 3 hours (based on current condition)

        rain_prob = {
            "clear": 5,  # Sunny now → 5% chance of rain
            "cloudy": 20,  # Overcast → 20% chance
            "rain": 80,  # Raining → 80% will continue
            "heavy_rain": 95,  # Downpour → 95% will continue
            "fog": 30,  # Foggy → 30% might rain
            "storm": 90,  # Storm → 90% will continue
        }[condition]

        # Visibility in km based on weather
        visibility = {
            "clear": 10,  # Excellent visibility
            "cloudy": 8,  # Good
            "rain": 5,  # Reduced (slow down)
            "heavy_rain": 3,  # Poor (dangerous)
            "fog": 2,  # Very poor (extreme caution)
            "storm": 2,  # Extremely poor (avoid driving)
        }[condition]

        return {
            "location": {"lat": lat, "lon": lon, "city": "Hyderabad"},
            "timestamp": datetime.now().isoformat(),
            "current": {
                "condition": condition,
                "temperature_c": temp,
                "humidity_percent": random.randint(40, 90),  # Random 40-90%
                "visibility_km": visibility,  # From lookup table
                "wind_speed_kmh": random.randint(5, 25),  # Random 5-25 km/h
            },
            "forecast_3hr": {
                "condition": random.choice(
                    WeatherSimulator.CONDITIONS
                ),  # Random future condition
                "rain_probability_percent": rain_prob,  # Based on current condition
            },
        }


class RoadDatabase:
    """Simulates road condition and accident database"""

    # Major roads in Telangana with realistic risk profiles
    ROADS = {
        "NH-44": {
            "name": "National Highway 44",
            "base_risk": 6.5,
            "total_accidents_6months": 15,
            "accidents_in_rain": 12,
            "potholes": 12,
            "width_m": 7.5,
            "traffic_level": "high",
            "last_maintenance": "2024-08-15",
        },
        "NH-163": {
            "name": "National Highway 163",
            "base_risk": 5.5,
            "total_accidents_6months": 8,
            "accidents_in_rain": 6,
            "potholes": 8,
            "width_m": 7.0,
            "traffic_level": "medium",
            "last_maintenance": "2024-10-01",
        },
        "SH-18": {
            "name": "State Highway 18",
            "base_risk": 3.5,
            "total_accidents_6months": 2,
            "accidents_in_rain": 1,
            "potholes": 3,
            "width_m": 6.0,
            "traffic_level": "low",
            "last_maintenance": "2024-11-20",
        },
        "ORR": {
            "name": "Outer Ring Road",
            "base_risk": 4.0,
            "total_accidents_6months": 10,
            "accidents_in_rain": 7,
            "potholes": 5,
            "width_m": 8.0,
            "traffic_level": "high",
            "last_maintenance": "2024-09-10",
        },
    }

    @staticmethod
    def get_road_info(road_name: str) -> Dict:
        """Get road information from database"""
        road = RoadDatabase.ROADS.get(  # If road not found, return default values
            road_name,
            {
                "name": road_name,
                "base_risk": 5.0,
                "total_accidents_6months": 5,
                "accidents_in_rain": 3,
                "potholes": 5,
                "width_m": 7.0,
                "traffic_level": "medium",
                "last_maintenance": "2024-06-01",
            },
        )
        return road

    @staticmethod
    def calculate_risk_score(
        road_name: str, weather: str, time_of_day: str = "day"
    ) -> Dict:
        """
        Calculate dynamic risk score based on road + weather + time

        Returns risk score 0-10 (10 = most dangerous)
        """

        road = RoadDatabase.get_road_info(road_name)
        base_risk = road["base_risk"]

        # Weather multipliers
        # How much does weather increase risk?
        weather_multiplier = {
            "clear": 1.0,
            "cloudy": 1.1,
            "fog": 1.5,
            "rain": 1.8,
            "heavy_rain": 2.2,
            "storm": 2.5,
        }.get(weather, 1.0)

        # Time of day multiplier
        time_multiplier = {"day": 1.0, "night": 1.3, "dawn": 1.2, "dusk": 1.2}.get(
            time_of_day, 1.0
        )

        # Calculate final risk
        final_risk = min(
            10.0, base_risk * weather_multiplier * time_multiplier
        )  # Capped at 10!

        # Determine risk category
        if final_risk >= 8.0:
            category = "VERY_HIGH"
            recommendation = "AVOID - Use alternative route"
        elif final_risk >= 6.0:
            category = "HIGH"
            recommendation = "CAUTION - Drive carefully, reduce speed"
        elif final_risk >= 4.0:
            category = "MEDIUM"
            recommendation = "MODERATE - Normal precautions"
        else:
            category = "LOW"
            recommendation = "SAFE - Normal conditions"

        return {
            "road_name": road_name,
            "risk_score": round(final_risk, 1),
            "risk_category": category,
            "base_risk": base_risk,
            "weather_factor": weather_multiplier,
            "time_factor": time_multiplier,
            "recommendation": recommendation,
            "contributing_factors": RoadDatabase._get_factors(
                road, weather, final_risk
            ),
        }

    @staticmethod
    def _get_factors(road: Dict, weather: str, risk_score: float) -> List[str]:
        """Identify risk factors"""
        factors = []

        if road["potholes"] > 10:
            factors.append(f"Many potholes ({road['potholes']})")

        if road["accidents_in_rain"] > 5 and weather in ["rain", "heavy_rain"]:
            factors.append(
                f"High rain accident rate ({road['accidents_in_rain']} in 6 months)"
            )

        if road["traffic_level"] == "high":
            factors.append("Heavy traffic congestion")

        if weather in ["heavy_rain", "storm"]:
            factors.append(f"Severe weather ({weather})")

        if road["width_m"] < 7:
            factors.append(f"Narrow road ({road['width_m']}m)")

        return factors

    @staticmethod
    def find_alternative_route(current_road: str, weather: str) -> Dict:
        """Find safer alternative route"""
        current_risk = RoadDatabase.calculate_risk_score(current_road, weather)[
            "risk_score"
        ]

        alternatives = []
        for road_name in RoadDatabase.ROADS.keys():
            if road_name != current_road:
                risk_data = RoadDatabase.calculate_risk_score(road_name, weather, "day")
                alternatives.append(
                    {
                        "road": road_name,
                        "risk_score": risk_data["risk_score"],
                        "risk_reduction": round(
                            current_risk - risk_data["risk_score"], 1
                        ),
                        "recommendation": risk_data["recommendation"],
                    }
                )

        # Sort by lowest risk
        alternatives.sort(key=lambda x: x["risk_score"])

        return {
            "current_road": current_road,
            "current_risk": current_risk,
            "alternatives": alternatives[:2],  # Top 2 alternatives
        }
