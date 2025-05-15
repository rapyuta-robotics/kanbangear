import logging
import os

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Log to the same file as logging_utils.py
log_file = "logs/hardware_changes.log"

# Get log level from environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Log to logs/hardware_changes.log file
        logging.StreamHandler()  # Also log to console
    ]
)