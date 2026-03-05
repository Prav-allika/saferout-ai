"""
Emergency Responder Agent
Handles critical situations and executes emergency protocols
"""

from typing import Dict, List
from datetime import datetime  # timestamp emergency events


class EmergencyResponderAgent:
    """Agent that handles critical emergencies"""

    def __init__(self):
        self.emergency_history = []
        self.total_emergencies = 0

    def handle_emergency(self, alert: Dict, vehicle_data: Dict) -> Dict:
        """
        Execute emergency response protocol

        Args:
            alert: The critical alert
            vehicle_data: Complete vehicle sensor data

        Returns:
            Emergency response actions
        """
        self.total_emergencies += 1  # increment when a new emergency is handled

        vehicle_id = vehicle_data["vehicle_id"]
        timestamp = datetime.now().isoformat()

        # Determine emergency type
        emergency_type = self._classify_emergency(alert)

        # Execute appropriate protocol
        if emergency_type == "TIRE_CRITICAL":
            actions = self._tire_critical_protocol(alert, vehicle_data)
        elif emergency_type == "ENGINE_CRITICAL":
            actions = self._engine_critical_protocol(alert, vehicle_data)
        elif emergency_type == "MULTIPLE_FAILURES":
            actions = self._multiple_failure_protocol(alert, vehicle_data)
        else:
            actions = self._general_emergency_protocol(alert, vehicle_data)

        # Create emergency record
        emergency_record = {
            "emergency_id": f"EMG-{self.total_emergencies:04d}",
            "vehicle_id": vehicle_id,
            "timestamp": timestamp,
            "type": emergency_type,
            "severity": "CRITICAL",
            "alert": alert,
            "actions_taken": actions,
            "status": "ACTIVE",
        }

        # Log emergency
        self.emergency_history.append(emergency_record)

        return emergency_record

    def _classify_emergency(self, alert: Dict) -> str:
        """Classify type of emergency"""
        alert_type = alert.get("type", "UNKNOWN")

        if "TIRE_CRITICAL" in alert_type:
            return "TIRE_CRITICAL"
        elif "ENGINE_CRITICAL" in alert_type:
            return "ENGINE_CRITICAL"
        elif isinstance(alert.get("alerts"), list) and len(alert["alerts"]) >= 2:
            return "MULTIPLE_FAILURES"
        else:
            return "GENERAL_EMERGENCY"

    def _tire_critical_protocol(self, alert, vehicle_data) -> List[Dict]:
        """Execute tire failure emergency protocol"""
        vehicle_id = vehicle_data["vehicle_id"]

        actions = [
            {
                "action": "SEND_URGENT_SMS",
                "target": "DRIVER",
                "message": f"🚨 CRITICAL: Tire failure imminent! Stop safely immediately. Do NOT continue driving.",
                "priority": "IMMEDIATE",
                "status": "EXECUTED",
            },
            {
                "action": "CALL_GARAGE",
                "target": "NEAREST_GARAGE",
                "message": f"Emergency tire service needed for vehicle {vehicle_id}. Current location: GPS coordinates attached.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
            {
                "action": "NOTIFY_MANAGER",
                "target": "FLEET_MANAGER",
                "message": f"Vehicle {vehicle_id} - CRITICAL tire failure. Driver alerted, garage called. Vehicle stopped.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
            {
                "action": "LOG_CRITICAL_EVENT",
                "target": "SYSTEM",
                "message": f"Emergency protocol activated: Tire critical failure on {vehicle_id}",
                "priority": "MEDIUM",
                "status": "EXECUTED",
            },
            {
                "action": "DISABLE_VEHICLE_START",
                "target": "VEHICLE_SYSTEM",
                "message": "Vehicle start disabled until tire replacement confirmed",
                "priority": "HIGH",
                "status": "PENDING",
            },
        ]

        return actions

    def _engine_critical_protocol(self, alert, vehicle_data) -> List[Dict]:
        """Execute engine failure emergency protocol"""
        vehicle_id = vehicle_data["vehicle_id"]
        engine_temp = vehicle_data["engine"]["engine_temp_c"]
        coolant = vehicle_data["engine"]["coolant_percent"]

        actions = [
            {
                "action": "SEND_URGENT_SMS",
                "target": "DRIVER",
                "message": f"🚨 ENGINE OVERHEATING! {engine_temp}°C! Turn on hazard lights. Pull over IMMEDIATELY. Turn off engine. DO NOT restart.",
                "priority": "IMMEDIATE",
                "status": "EXECUTED",
            },
            {
                "action": "CALL_EMERGENCY_MECHANIC",
                "target": "ROADSIDE_ASSISTANCE",
                "message": f"Engine overheat emergency - {vehicle_id}. Temp: {engine_temp}°C, Coolant: {coolant}%. Tow needed.",
                "priority": "CRITICAL",
                "status": "EXECUTED",
            },
            {
                "action": "NOTIFY_MANAGER",
                "target": "FLEET_MANAGER",
                "message": f"CRITICAL: {vehicle_id} engine overheat ({engine_temp}°C). Vehicle stopped. Tow truck dispatched.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
            {
                "action": "NOTIFY_PASSENGERS",
                "target": "PASSENGERS",
                "message": "Emergency stop - engine issue. Please remain calm. Assistance is on the way.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
            {
                "action": "LOG_CRITICAL_EVENT",
                "target": "SYSTEM",
                "message": f"Emergency protocol: Engine critical on {vehicle_id} - {engine_temp}°C",
                "priority": "MEDIUM",
                "status": "EXECUTED",
            },
        ]

        return actions

    def _multiple_failure_protocol(self, alert, vehicle_data) -> List[Dict]:
        """Execute multiple system failure protocol"""
        vehicle_id = vehicle_data["vehicle_id"]

        actions = [
            {
                "action": "SEND_URGENT_SMS",
                "target": "DRIVER",
                "message": "🚨 MULTIPLE SYSTEM FAILURES! Stop vehicle immediately in safe location.",
                "priority": "IMMEDIATE",
                "status": "EXECUTED",
            },
            {
                "action": "CALL_EMERGENCY_SERVICES",
                "target": "DISPATCH",
                "message": f"Multiple critical failures on {vehicle_id}. Immediate assistance required.",
                "priority": "CRITICAL",
                "status": "EXECUTED",
            },
            {
                "action": "NOTIFY_MANAGER",
                "target": "FLEET_MANAGER",
                "message": f"CRITICAL: Multiple system failures on {vehicle_id}. Emergency response activated.",
                "priority": "CRITICAL",
                "status": "EXECUTED",
            },
        ]

        return actions

    def _general_emergency_protocol(self, alert, vehicle_data) -> List[Dict]:
        """General emergency protocol for unclassified emergencies"""
        vehicle_id = vehicle_data["vehicle_id"]

        actions = [
            {
                "action": "SEND_URGENT_SMS",
                "target": "DRIVER",
                "message": "⚠️ Critical vehicle issue detected. Please stop safely and await instructions.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
            {
                "action": "NOTIFY_MANAGER",
                "target": "FLEET_MANAGER",
                "message": f"Critical alert on {vehicle_id}. Emergency response initiated.",
                "priority": "HIGH",
                "status": "EXECUTED",
            },
        ]

        return actions

    # get the active emergencies and info about them from emergency history
    def get_emergency_summary(self) -> Dict:
        """Get summary of all emergencies"""
        active_emergencies = [
            e for e in self.emergency_history if e["status"] == "ACTIVE"
        ]

        emergency_types = {}
        for emergency in self.emergency_history:
            etype = emergency["type"]
            emergency_types[etype] = emergency_types.get(etype, 0) + 1

        return {
            "total_emergencies": self.total_emergencies,
            "active_emergencies": len(active_emergencies),
            "emergency_types": emergency_types,
            "last_emergency": self.emergency_history[-1]
            if self.emergency_history
            else None,
        }
