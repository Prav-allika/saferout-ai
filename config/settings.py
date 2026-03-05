"""
Central configuration for SafeRoute AI
All settings in one place!
"""

# pydantic_settings, type safe config to catch errors and validate settings
from pydantic_settings import BaseSettings
import os  # For enironmental variable access


class Settings(BaseSettings):
    # Project Info(used in UI, logs and reports)
    PROJECT_NAME: str = "SafeRoute AI"
    VERSION: str = "1.0.0"  # Semantic Versioning: MAJOR.MINOR.PATCH

    # Simulation Settings
    # how ofter sensors update
    SENSOR_UPDATE_INTERVAL: int = 5  # seconds
    NUM_VEHICLES: int = 50

    # ML Model Settings
    TIRE_FAILURE_THRESHOLD: float = (
        0.7  # 70% probability, Minimum probability (0-1) to predict tire failure
    )
    ROUTE_RISK_THRESHOLD: float = (
        6.0  # Out of 10, Route risk score (0-10) triggering warnings
    )

    # Agent Settings (can be overridden with environment variables)
    ORCHESTRATOR_MODEL: str = os.getenv("LLM_MODEL", "llama3.1:70b")
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMP", "0.0"))

    # Normal ranges (based on real sensor specs)
    TIRE_PRESSURE_NORMAL: tuple = (32, 35)  # PSI
    TIRE_TEMP_NORMAL: tuple = (35, 45)  # Celsius
    ENGINE_TEMP_NORMAL: tuple = (85, 95)  # Celsius

    # Logging Settings
    LOG_DIR: str = "logs"  # directory where log files are stored
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # min log level to display

    # Performance Settings
    MAX_SENSOR_HISTORY: int = 100  # Keep last N readings
    # Prevents memory leaks (old readings deleted)
    # Used by: data_processor.py for aggregation
    # Memory: ~50 KB per vehicle (100 readings × 500 bytes)
    PROCESSING_TIMEOUT_MS: int = 500  # Max time for processing

    class Config:
        case_sensitive = True  # environmental variables must match the exact case


# Create global settings instance
# All modules can access the settings via this instance
# Usage: from config.settings import settings
settings = Settings()
