"""
Orchestrator Agent - Complete Multi-Agent System
Coordinates all specialized agents: Tire Predictor, Emergency Responder, Route Analyzer
"""

from typing import Dict, List
from datetime import datetime
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from agents.tire_predictor import TirePredictorAgent  # ML predictions
from agents.emergency_responder import EmergencyResponderAgent  # Emergency protocols
from agents.route_analyzer import RouteAnalyzerAgent  # Route safety

# Route cache TTL: refresh analysis after this many ticks (~30 seconds at 1s interval)
_ROUTE_CACHE_TTL = 30


class Orchestrator:
    """Master controller that coordinates all specialized agents"""

    def __init__(self):
        self.alert_history = deque(maxlen=1000)  # Bounded: prevents memory leak

        # Initialize all specialized agents
        self.tire_predictor = TirePredictorAgent()  # → Ready to predict tire failures
        self.emergency_responder = (
            EmergencyResponderAgent()
        )  # → Ready to execute emergency protocols
        self.route_analyzer = RouteAnalyzerAgent()  # → Ready to analyze routes

        # Route cache: keyed by "road_name_time_of_day", stores (result, tick_count)
        self._route_cache: Dict = {}

        print("Orchestrator initialized with ALL specialized agents:")
        print("   - Tire Predictor Agent (ML-powered failure prediction)")
        print("   - Emergency Responder Agent (Critical situation handler)")
        print("   - Route Analyzer Agent (Weather + Road safety)")

    def analyze_sensor_data(self, sensor_data: Dict, route_info: Dict = None) -> Dict:
        """
        Analyze incoming sensor data and coordinate agents.
        Route analysis, tire checks, and engine checks run in parallel.

        Args:
            sensor_data: Vehicle sensor readings
            route_info: Optional route information (road, time, location)

        Returns:
            Dict with decisions, alerts, and agent responses
        """
        vehicle_id = sensor_data["vehicle_id"]
        timestamp = sensor_data["timestamp"]

        decisions = {
            "vehicle_id": vehicle_id,
            "timestamp": timestamp,
            "alerts": [],
            "actions": [],
            "risk_level": "LOW",
            "agent_responses": {},
        }

        # 1. RUN ROUTE + TIRE + ENGINE CHECKS IN PARALLEL
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit tire and engine checks (always run)
            future_tires = executor.submit(
                self._check_tires, sensor_data["tires"], sensor_data["metadata"]
            )
            future_engine = executor.submit(self._check_engine, sensor_data["engine"])

            # Submit route analysis with caching (only re-run after TTL expires)
            future_route = None
            route_key = None
            if route_info:
                route_key = f"{route_info.get('road_name')}_{route_info.get('time_of_day')}"
                cached = self._route_cache.get(route_key)
                if cached and cached["ticks"] < _ROUTE_CACHE_TTL:
                    # Use cached result, increment tick counter
                    self._route_cache[route_key]["ticks"] += 1
                    route_analysis = cached["result"]
                else:
                    # Cache expired or missing — fetch fresh
                    future_route = executor.submit(
                        self.route_analyzer.analyze_route, route_info
                    )

            tire_alerts = future_tires.result()
            engine_alerts = future_engine.result()

            if future_route is not None:
                route_analysis = future_route.result()
                self._route_cache[route_key] = {"result": route_analysis, "ticks": 0}

        # 2. PROCESS ROUTE RESULTS
        if route_info:
            decisions["agent_responses"]["route_analyzer"] = route_analysis
            if route_analysis["risk_analysis"]["risk_score"] >= 6.0:
                decisions["alerts"].append(
                    {
                        "type": "ROUTE_HIGH_RISK",
                        "message": f"Route {route_info['road_name']}: High risk ({route_analysis['risk_analysis']['risk_score']}/10)",
                        "severity": "WARNING",
                        "recommended_action": "CONSIDER_ALTERNATIVE",
                    }
                )

        # 3. PROCESS TIRE RESULTS
        if tire_alerts:
            decisions["alerts"].extend(tire_alerts)
            decisions["risk_level"] = self._calculate_risk_level(tire_alerts)

        # 4. PROCESS ENGINE RESULTS
        if engine_alerts:
            decisions["alerts"].extend(engine_alerts)
            engine_risk = self._calculate_risk_level(engine_alerts)
            _risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
            # Take the higher of tire risk and engine risk
            if _risk_order[engine_risk] > _risk_order[decisions["risk_level"]]:
                decisions["risk_level"] = engine_risk

        # 5. ROUTE TO SPECIALIZED AGENTS BASED ON RISK
        if decisions["risk_level"] == "HIGH":
            # CRITICAL - Activate Emergency Responder
            emergency_response = self.emergency_responder.handle_emergency(
                decisions["alerts"][0],
                sensor_data,
            )
            decisions["agent_responses"]["emergency_responder"] = emergency_response
            decisions["actions"] = [
                action["action"] for action in emergency_response["actions_taken"]
            ]

        elif decisions["risk_level"] == "MEDIUM":
            # WARNING - Get ML prediction from Tire Predictor
            for alert in decisions["alerts"]:
                if "TIRE" in alert.get("type", ""):
                    tire_position = alert["position"]
                    tire_data = sensor_data["tires"][tire_position]
                    prediction = self.tire_predictor.analyze(
                        tire_data, sensor_data["metadata"]
                    )
                    decisions["agent_responses"]["tire_predictor"] = prediction
                    ml_rec = prediction["ml_prediction"]["recommendation"]
                    decisions["actions"].append(f"ML_PREDICTION: {ml_rec}")
                    break

            decisions["actions"].extend(
                ["SEND_WARNING_SMS", "SCHEDULE_SERVICE", "LOG_WARNING"]
            )

        else:
            decisions["actions"] = ["LOG_NORMAL"]

        # 6. COMBINE ROUTE RISK WITH VEHICLE RISK
        if route_info and "route_analyzer" in decisions["agent_responses"]:
            route_risk = decisions["agent_responses"]["route_analyzer"][
                "risk_analysis"
            ]["risk_score"]
            if route_risk >= 8.0 and decisions["risk_level"] != "HIGH":
                decisions["actions"].append("ROUTE_WARNING: Extreme route conditions")

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
