"""
System Monitoring Utility
Tracks system performance, metrics, and health
"""

from typing import Dict, List
from datetime import datetime, timedelta
import time


class SystemMonitor:
    """Monitors system performance and health"""

    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            "sensor_readings_processed": 0,
            "alerts_generated": 0,
            "critical_alerts": 0,
            "warnings": 0,
            "ml_predictions": 0,
            "emergencies_handled": 0,
            "route_analyses": 0,
            "errors": 0,
        }

        self.performance_log = []

    def record_sensor_reading(self, processing_time_ms: float = None):
        """Record a sensor reading processed"""
        self.metrics["sensor_readings_processed"] += 1

        if processing_time_ms:
            self.performance_log.append(
                {
                    "type": "sensor_reading",
                    "timestamp": datetime.now(),
                    "duration_ms": processing_time_ms,
                }
            )

    def record_alert(self, severity: str):
        """Record an alert generated"""
        self.metrics["alerts_generated"] += 1

        if severity == "CRITICAL":
            self.metrics["critical_alerts"] += 1
        elif severity == "WARNING":
            self.metrics["warnings"] += 1

    def record_ml_prediction(self):
        """Record ML prediction made"""
        self.metrics["ml_predictions"] += 1

    def record_emergency(self):
        """Record emergency handled"""
        self.metrics["emergencies_handled"] += 1

    def record_route_analysis(self):
        """Record route analysis performed"""
        self.metrics["route_analyses"] += 1

    def record_error(self):
        """Record system error"""
        self.metrics["errors"] += 1

    def get_uptime(self) -> str:
        """Get system uptime"""
        uptime = datetime.now() - self.start_time

        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60

        return f"{uptime.days}d {hours}h {minutes}m {seconds}s"

    def get_metrics(self) -> Dict:
        """Get current system metrics"""
        return {
            "uptime": self.get_uptime(),
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            **self.metrics,
        }

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        if not self.performance_log:
            return {
                "avg_processing_time_ms": 0,
                "max_processing_time_ms": 0,
                "min_processing_time_ms": 0,
            }

        durations = [log["duration_ms"] for log in self.performance_log]

        return {
            "avg_processing_time_ms": round(sum(durations) / len(durations), 2),
            "max_processing_time_ms": round(max(durations), 2),
            "min_processing_time_ms": round(min(durations), 2),
            "total_operations": len(durations),
        }

    def get_health_status(self) -> Dict:
        """Get system health status"""
        # Calculate error rate
        total_operations = self.metrics["sensor_readings_processed"]
        error_rate = (
            (self.metrics["errors"] / total_operations * 100)
            if total_operations > 0
            else 0
        )

        # Determine health
        if error_rate > 5:
            health = "UNHEALTHY"
        elif error_rate > 1:
            health = "DEGRADED"
        else:
            health = "HEALTHY"

        return {
            "status": health,
            "error_rate_percent": round(error_rate, 2),
            "uptime": self.get_uptime(),
            "critical_alerts_active": self.metrics["critical_alerts"],
            "last_check": datetime.now().isoformat(),
        }

    def generate_report(self) -> str:
        """Generate human-readable monitoring report"""
        metrics = self.get_metrics()
        performance = self.get_performance_stats()
        health = self.get_health_status()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SafeRoute AI - System Monitoring Report            ║
╚══════════════════════════════════════════════════════════════╝

⏱️  UPTIME: {metrics["uptime"]}
📊 HEALTH: {health["status"]} (Error Rate: {health["error_rate_percent"]}%)

📈 METRICS:
  • Sensor Readings Processed: {metrics["sensor_readings_processed"]}
  • Alerts Generated: {metrics["alerts_generated"]}
    - Critical: {metrics["critical_alerts"]}
    - Warnings: {metrics["warnings"]}
  • ML Predictions: {metrics["ml_predictions"]}
  • Emergencies Handled: {metrics["emergencies_handled"]}
  • Route Analyses: {metrics["route_analyses"]}
  • Errors: {metrics["errors"]}

⚡ PERFORMANCE:
  • Avg Processing Time: {performance["avg_processing_time_ms"]} ms
  • Max Processing Time: {performance["max_processing_time_ms"]} ms
  • Min Processing Time: {performance["min_processing_time_ms"]} ms
  • Total Operations: {performance["total_operations"]}

═══════════════════════════════════════════════════════════════
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
═══════════════════════════════════════════════════════════════
        """

        return report
