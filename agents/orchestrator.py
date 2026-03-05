"""
Orchestrator Agent - Complete Multi-Agent System
Coordinates all specialized agents: Tire Predictor, Emergency Responder, Route Analyzer
"""

from typing import Dict, List
from datetime import datetime
from agents.tire_predictor import TirePredictorAgent  # ML predictions
from agents.emergency_responder import EmergencyResponderAgent  # Emergency protocols
from agents.route_analyzer import RouteAnalyzerAgent  # Route safety


class Orchestrator:
    """Master controller that coordinates all specialized agents"""

    def __init__(self):
        self.alert_history = []  # → Stores all alerts for tracking

        # Initialize all specialized agents
        self.tire_predictor = TirePredictorAgent()  # → Ready to predict tire failures
        self.emergency_responder = (
            EmergencyResponderAgent()
        )  # → Ready to execute emergency protocols
        self.route_analyzer = RouteAnalyzerAgent()  # → Ready to analyze routes

        print("Orchestrator initialized with ALL specialized agents:")
        print("   - Tire Predictor Agent (ML-powered failure prediction)")
        print("   - Emergency Responder Agent (Critical situation handler)")
        print("   - Route Analyzer Agent (Weather + Road safety)")

    def analyze_sensor_data(self, sensor_data: Dict, route_info: Dict = None) -> Dict:
        """
        Analyze incoming sensor data and coordinate agents

        Args:
            sensor_data: Vehicle sensor readings
            route_info: Optional route information (road, time, location)

        Returns:
            Dict with decisions, alerts, and agent responses
        """
        vehicle_id = sensor_data["vehicle_id"]
        timestamp = sensor_data["timestamp"]

        # Storage for decisions
        decisions = {
            "vehicle_id": vehicle_id,
            "timestamp": timestamp,
            "alerts": [],
            "actions": [],
            "risk_level": "LOW",
            "agent_responses": {},
        }

        # 1. ROUTE ANALYSIS (if route provided)
        if route_info:
            route_analysis = self.route_analyzer.analyze_route(route_info)
            decisions["agent_responses"]["route_analyzer"] = route_analysis

            # Check if route is high risk
            if route_analysis["risk_analysis"]["risk_score"] >= 6.0:
                decisions["alerts"].append(
                    {
                        "type": "ROUTE_HIGH_RISK",
                        "message": f"Route {route_info['road_name']}: High risk ({route_analysis['risk_analysis']['risk_score']}/10)",
                        "severity": "WARNING",
                        "recommended_action": "CONSIDER_ALTERNATIVE",
                    }
                )

        # 2. TIRE SENSOR ANALYSIS
        # Call helper function to check all 4 tires:

        tire_alerts = self._check_tires(sensor_data["tires"], sensor_data["metadata"])
        if tire_alerts:
            decisions["alerts"].extend(tire_alerts)
            decisions["risk_level"] = self._calculate_risk_level(tire_alerts)

        # 3. ENGINE ANALYSIS
        engine_alerts = self._check_engine(sensor_data["engine"])
        if engine_alerts:
            decisions["alerts"].extend(engine_alerts)
            # Engine issues escalate risk
            if decisions["risk_level"] == "LOW":
                decisions["risk_level"] = "MEDIUM"
            elif decisions["risk_level"] == "MEDIUM":
                decisions["risk_level"] = "HIGH"

        # 4. ROUTE TO SPECIALIZED AGENTS BASED ON RISK
        if decisions["risk_level"] == "HIGH":
            # CRITICAL - Activate Emergency Responder
            emergency_response = self.emergency_responder.handle_emergency(
                decisions["alerts"][0],
                sensor_data,  # First CRITICAL alert
            )
            decisions["agent_responses"]["emergency_responder"] = emergency_response
            decisions["actions"] = [
                action["action"] for action in emergency_response["actions_taken"]
            ]

        elif decisions["risk_level"] == "MEDIUM":
            # WARNING - Get ML prediction from Tire Predictor
            for alert in decisions["alerts"]:
                if "TIRE" in alert.get("type", ""):  # Found tire alert!
                    tire_position = alert["position"]  # "front_left"
                    tire_data = sensor_data["tires"][tire_position]

                    prediction = self.tire_predictor.analyze(
                        tire_data, sensor_data["metadata"]
                    )
                    decisions["agent_responses"]["tire_predictor"] = prediction

                    # Add ML prediction to actions
                    ml_rec = prediction["ml_prediction"]["recommendation"]
                    decisions["actions"].append(f"ML_PREDICTION: {ml_rec}")
                    # decisions["actions"] = ["ML_PREDICTION: SERVICE_TODAY"]
                    break

            # Add standard warning actions
            decisions["actions"].extend(
                ["SEND_WARNING_SMS", "SCHEDULE_SERVICE", "LOG_WARNING"]
            )

        else:
            # LOW risk - Just log
            decisions["actions"] = ["LOG_NORMAL"]

        # 5. COMBINE ROUTE RISK WITH VEHICLE RISK
        if route_info and "route_analyzer" in decisions["agent_responses"]:
            route_risk = decisions["agent_responses"]["route_analyzer"][
                "risk_analysis"
            ]["risk_score"]
            if route_risk >= 8.0 and decisions["risk_level"] != "HIGH":
                decisions["actions"].append("ROUTE_WARNING: Extreme route conditions")

        # Log alert
        if decisions["alerts"]:
            self.alert_history.append(decisions)

        return decisions

    def _check_tires(self, tires: Dict, metadata: Dict) -> List[Dict]:
        """Check all tire sensors for issues"""
        alerts = []

        for position, tire_data in tires.items():
            pressure = tire_data["pressure_psi"]
            temp = tire_data["temperature_c"]

            # Critical pressure
            if pressure < 28:
                alerts.append(
                    {
                        "type": "TIRE_CRITICAL",
                        "position": position,
                        "message": f"Tire {position}: CRITICAL pressure {pressure} PSI",
                        "severity": "CRITICAL",
                        "recommended_action": "IMMEDIATE_SERVICE",
                    }
                )

            # Warning pressure
            elif pressure < 30:
                alerts.append(
                    {
                        "type": "TIRE_WARNING",
                        "position": position,
                        "message": f"Tire {position}: Low pressure {pressure} PSI",
                        "severity": "WARNING",
                        "recommended_action": "SERVICE_SOON",
                    }
                )

            # High temperature
            if temp > 50:
                alerts.append(
                    {
                        "type": "TIRE_OVERHEAT",
                        "position": position,
                        "message": f"Tire {position}: High temperature {temp}°C",
                        "severity": "WARNING",
                        "recommended_action": "CHECK_TIRE",
                    }
                )

        return alerts

    def _check_engine(self, engine_data: Dict) -> List[Dict]:
        """Check engine sensor for issues"""
        alerts = []

        temp = engine_data["engine_temp_c"]
        coolant = engine_data["coolant_percent"]

        # Critical overheat
        if temp > 110:
            alerts.append(
                {
                    "type": "ENGINE_CRITICAL",
                    "message": f"Engine CRITICAL: {temp}°C, Coolant: {coolant}%",
                    "severity": "CRITICAL",
                    "recommended_action": "STOP_VEHICLE",
                }
            )

        # Warning overheat
        elif temp > 100:
            alerts.append(
                {
                    "type": "ENGINE_WARNING",
                    "message": f"Engine overheating: {temp}°C",
                    "severity": "WARNING",
                    "recommended_action": "MONITOR_CLOSELY",
                }
            )

        # Low coolant
        if coolant < 30:
            alerts.append(
                {
                    "type": "COOLANT_LOW",
                    "message": f"Low coolant: {coolant}%",
                    "severity": "WARNING",
                    "recommended_action": "ADD_COOLANT",
                }
            )

        return alerts

    def _calculate_risk_level(self, alerts: List[Dict]) -> str:
        """Calculate overall risk level from alerts"""
        if not alerts:
            return "LOW"

        # Check for any CRITICAL alerts
        for alert in alerts:
            if alert["severity"] == "CRITICAL":
                return "HIGH"

        # Check for multiple WARNING alerts
        if len(alerts) >= 2:
            return "MEDIUM"

        return "MEDIUM"

    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts and agent performance"""
        total_alerts = len(self.alert_history)

        critical_count = sum(
            1 for decision in self.alert_history if decision["risk_level"] == "HIGH"
        )

        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_count,
            "last_alert": self.alert_history[-1] if self.alert_history else None,
            "agent_stats": {
                "tire_predictor": {
                    "predictions_made": self.tire_predictor.predictions_made
                },
                "emergency_responder": {
                    "total_emergencies": self.emergency_responder.total_emergencies
                },
                "route_analyzer": {
                    "analyses_performed": self.route_analyzer.analyses_performed,
                    "high_risk_routes": sum(
                        1
                        for a in self.route_analyzer.route_history
                        if a["risk_analysis"]["risk_score"] >= 6.0
                    ),
                },
            },
        }
