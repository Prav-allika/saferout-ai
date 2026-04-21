"""
Central configuration for SafeRoute AI
All settings in one place!
"""

import os


class Settings:
    # Project Info
    PROJECT_NAME: str = "SafeRoute AI"
    VERSION: str = "1.0.0"

    # Simulation Settings
    SENSOR_UPDATE_INTERVAL: int = 5  # seconds
    NUM_VEHICLES: int = 50

    # ML Model Settings
    TIRE_FAILURE_THRESHOLD: float = 0.7   # 70% probability threshold
    ROUTE_RISK_THRESHOLD: float = 6.0     # out of 10

    # Agent Settings (can be overridden with environment variables)
    ORCHESTRATOR_MODEL: str = os.getenv("LLM_MODEL", "llama3.3:70b")
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMP", "0.0"))

    # Normal sensor ranges (based on real sensor specs)
    TIRE_PRESSURE_NORMAL: tuple = (32, 35)   # PSI
    TIRE_TEMP_NORMAL: tuple = (35, 45)       # Celsius
    ENGINE_TEMP_NORMAL: tuple = (85, 95)     # Celsius

    # Logging Settings
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Performance Settings
    MAX_SENSOR_HISTORY: int = 100
    PROCESSING_TIMEOUT_MS: int = 500


# Global settings instance — import with: from config.settings import settings
settings = Settings()
