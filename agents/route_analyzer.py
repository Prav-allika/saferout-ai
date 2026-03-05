"""
Route Analyzer Agent
Analyzes route safety based on weather and road conditions
"""

from typing import Dict, List
from simulation.environment import WeatherSimulator, RoadDatabase


class RouteAnalyzerAgent:
    """Agent that analyzes route safety and suggests alternatives"""

    def __init__(self):
        self.analyses_performed = 0  # counter
        self.route_history = []  # list of past analyses

    def analyze_route(self, route_info: Dict) -> Dict:
        """
        Analyze route safety

        Args:
            route_info: Dict with road_name, time_of_day, vehicle_location

        Returns:
            Route analysis with safety recommendations
        """
        self.analyses_performed += 1  # increment
        # extract route info
        road_name = route_info.get("road_name", "NH-44")
        time_of_day = route_info.get("time_of_day", "day")
        location = route_info.get("location", {"lat": 17.3850, "lon": 78.4867})

        # Get weather data
        weather_data = WeatherSimulator.get_weather(location["lat"], location["lon"])
        current_weather = weather_data["current"]["condition"]

        # Calculate route risk, # Calls RoadDatabase from environment.py
        risk_analysis = RoadDatabase.calculate_risk_score(
            road_name, current_weather, time_of_day
        )

        # Get road details
        road_info = RoadDatabase.get_road_info(road_name)

        # Find alternatives if high risk
        alternatives = None
        if risk_analysis["risk_score"] >= 6.0:
            alternatives = RoadDatabase.find_alternative_route(
                road_name, current_weather
            )

        # Generate analysis
        analysis = {
            "agent": "RouteAnalyzerAgent",
            "timestamp": weather_data["timestamp"],
            "route": {
                "road_name": road_name,
                "road_type": road_info["name"],
                "time_of_day": time_of_day,
            },
            "weather": {
                "condition": current_weather,
                "temperature": weather_data["current"]["temperature_c"],
                "visibility_km": weather_data["current"]["visibility_km"],
                "rain_forecast": weather_data["forecast_3hr"][
                    "rain_probability_percent"
                ],
            },
            "risk_analysis": risk_analysis,
            "road_conditions": {
                "potholes": road_info["potholes"],
                "accidents_6months": road_info["total_accidents_6months"],
                "accidents_in_rain": road_info["accidents_in_rain"],
                "traffic_level": road_info["traffic_level"],
            },
            "alternatives": alternatives,
            "recommendation": self._generate_recommendation(
                risk_analysis, weather_data, alternatives
            ),
        }

        # Store in history
        self.route_history.append(analysis)

        return analysis

    def _generate_recommendation(self, risk_analysis, weather_data, alternatives):
        """Generate human-readable recommendation"""
        risk_score = risk_analysis["risk_score"]
        weather = weather_data["current"]["condition"]
        visibility = weather_data["current"]["visibility_km"]

        if risk_score >= 8.0:
            if alternatives:
                alt_road = alternatives["alternatives"][0][
                    "road"
                ]  # Get alternative road name
                reduction = alternatives["alternatives"][0][
                    "risk_reduction"
                ]  # Get risk reduction value
                rec = f"🚨 AVOID THIS ROUTE! Risk: {risk_score}/10. Use {alt_road} instead (reduces risk by {reduction} points). "
            else:
                rec = f"🚨 EXTREME CAUTION! Risk: {risk_score}/10. Delay trip if possible. "

            if weather in ["heavy_rain", "storm"]:
                rec += "Severe weather conditions. "
            if visibility < 3:
                rec += "Very poor visibility. "

        elif risk_score >= 6.0:
            rec = f"⚠️ HIGH RISK: {risk_score}/10. {risk_analysis['recommendation']}. "
            if weather == "rain":
                rec += "Rain increases accident risk significantly on this road. "
            if alternatives:
                alt_road = alternatives["alternatives"][0]["road"]
                rec += f"Consider {alt_road} as safer alternative. "

        elif risk_score >= 4.0:
            rec = f"⚡ MODERATE RISK: {risk_score}/10. Exercise normal caution. "
            if len(risk_analysis["contributing_factors"]) > 0:
                rec += f"Watch for: {', '.join(risk_analysis['contributing_factors'][:2])}. "
        else:
            rec = f"LOW RISK: {risk_score}/10. Safe to proceed. Good visibility, clear conditions. "

        return rec

    # get the sum and average risk scores
    def get_analysis_summary(self) -> Dict:
        """Get summary of route analyses"""
        if not self.route_history:
            return {"analyses_performed": 0, "high_risk_routes": 0, "average_risk": 0}

        high_risk = sum(
            1 for a in self.route_history if a["risk_analysis"]["risk_score"] >= 6.0
        )
        avg_risk = sum(
            a["risk_analysis"]["risk_score"] for a in self.route_history
        ) / len(self.route_history)

        return {
            "analyses_performed": self.analyses_performed,
            "high_risk_routes": high_risk,
            "average_risk": round(avg_risk, 1),
            "last_analysis": self.route_history[-1] if self.route_history else None,
        }
