"""
Logging Utility for SafeRoute AI
Provides structured logging with different levels and output formats
"""

import logging  # built in logging module
import os  # create log directories
from datetime import datetime  # timestamp log files
from typing import Dict, Any
import json  # format complex data


class SafeRouteLogger:
    """Custom logger for SafeRoute AI system"""

    def __init__(self, name: str = "SafeRoute", log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir

        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)  # exist_ok=True prevents crash if exists

        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(
            logging.DEBUG
        )  # Captures EVERYTHING (DEBUG is lowest level)
        # Handlers decide what to actually show/save

        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()  # remove existing handlers

        # Console handler (INFO and above) #quick, immediate, minimal info
        console_handler = logging.StreamHandler()  # print to console
        console_handler.setLevel(logging.INFO)  # only show INFO and above
        console_formatter = logging.Formatter(  # format for console output
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler - All logs (keep detailed logs for debugging and historical analysis)
        log_file = os.path.join(  # log file for all logs
            log_dir, f"saferout_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # captures all logs
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",  # saferout_20250218.log
        )
        file_handler.setFormatter(file_formatter)  # format for file output
        self.logger.addHandler(file_handler)  # add file handler to logger

        # Critical events file (separate file for CRITICAL/ERROR)
        critical_file = os.path.join(
            log_dir, f"critical_{datetime.now().strftime('%Y%m%d')}.log"
        )
        critical_handler = logging.FileHandler(critical_file)
        critical_handler.setLevel(logging.ERROR)
        critical_handler.setFormatter(file_formatter)
        self.logger.addHandler(
            critical_handler
        )  #######how to decide what is critical and normal logs

        self.logger.info(f"Logger initialized: {name}")

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        extra_info = self._format_kwargs(kwargs)  # format dict/list of kwargs
        self.logger.debug(f"{message} {extra_info}")

    def info(self, message: str, **kwargs):
        """Log info message"""
        extra_info = self._format_kwargs(kwargs)
        self.logger.info(f"{message} {extra_info}")

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        extra_info = self._format_kwargs(kwargs)
        self.logger.warning(f"{message} {extra_info}")

    def error(self, message: str, **kwargs):
        """Log error message"""
        extra_info = self._format_kwargs(kwargs)
        self.logger.error(f"{message} {extra_info}")

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        extra_info = self._format_kwargs(kwargs)
        self.logger.critical(f"{message} {extra_info}")

    def log_alert(self, alert: Dict[str, Any]):  # alert specific logging
        """Log alert with structured data"""
        alert_str = json.dumps(alert, indent=2)
        severity = alert.get("severity", "UNKNOWN")
        # automatically choose log level based on severity
        if severity == "CRITICAL":
            self.critical(
                f"Alert triggered: {alert.get('message', 'No message')}",
                alert_data=alert_str,
            )
        elif severity == "WARNING":
            self.warning(
                f"Alert triggered: {alert.get('message', 'No message')}",
                alert_data=alert_str,
            )
        else:
            self.info(
                f"Alert triggered: {alert.get('message', 'No message')}",
                alert_data=alert_str,
            )

    # Consistent format = Easy search!
    ## Sensor data is DEBUG (noisy, file only)
    def log_sensor_data(self, sensor_data: Dict[str, Any]):
        """Log sensor data (debug level)"""
        vehicle_id = sensor_data.get("vehicle_id", "UNKNOWN")
        self.debug(
            f"Sensor data received from {vehicle_id}",
            data=json.dumps(sensor_data, default=str),  # automatically debug
        )

    # Agent responses are INFO (important, show in console)
    def log_agent_response(self, agent_name: str, response: Dict[str, Any]):
        """Log agent response"""
        self.info(
            f"Agent response from {agent_name}",
            response=json.dumps(response, default=str),  # Automatically INFO
        )

    # Emergencies are CRITICAL (urgent, all outputs)
    def log_emergency(self, emergency: Dict[str, Any]):
        """Log emergency event (always CRITICAL)"""
        emergency_id = emergency.get("emergency_id", "UNKNOWN")
        emergency_type = emergency.get("type", "UNKNOWN")
        self.critical(
            f"EMERGENCY {emergency_id}: {emergency_type}",
            emergency_data=json.dumps(emergency, default=str),
        )

    def _format_kwargs(self, kwargs: Dict) -> str:
        """Format additional keyword arguments for logging"""
        if not kwargs:
            return ""

        formatted = []
        for key, value in kwargs.items():
            if isinstance(value, (dict, list)):
                # Complex types need JSON formatting
                formatted.append(f"{key}={json.dumps(value, default=str)}")
            else:
                # Simple types can be printed directly
                formatted.append(f"{key}={value}")

        return f"[{', '.join(formatted)}]" if formatted else ""  ##whats happening last


# Global logger instance
_global_logger = None  # Starts empty


# ensure one global logger instance present for entire project››
def get_logger(name: str = "SafeRoute") -> SafeRouteLogger:
    """Get or create global logger instance"""
    global _global_logger  # Access the global variable
    if _global_logger is None:
        # First time called - create logger
        _global_logger = SafeRouteLogger(name)
    # Return the SAME logger every time
    return _global_logger
