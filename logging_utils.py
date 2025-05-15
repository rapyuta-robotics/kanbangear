import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
log_filename = "logs/hardware_changes.log"

class AuthLogFilter(logging.Filter):
    """Filter to prevent authentication logs from cluttering the log file"""
    def filter(self, record):
        if "Authenticating user:" in record.getMessage():
            return False
        return True

def setup_logging():
    """Configure logging for the entire application"""
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Add filter to root logger to prevent authentication logs
    root_logger = logging.getLogger()
    root_logger.addFilter(AuthLogFilter())
    
    # Prevent Uvicorn logs from propagating
    logging.getLogger("uvicorn.access").propagate = False
    logging.getLogger("uvicorn.error").propagate = False

def log_hardware_changes(hardware, old_values, new_values, user_info):
    changes = {}
    for key, new_value in new_values.items():
        if key in old_values and old_values[key] != new_value:
            changes[key] = {'old': old_values[key], 'new': new_value}
    # Include 'reason' if provided
    reason = new_values.get('reason')
    if changes:
        changes_str = ", ".join([
            f"{field}: {change['old']} → {change['new']}"
            for field, change in changes.items() if field != 'reason'
        ])
        if reason:
            changes_str += f", Reason: {reason}"
        entity_name = getattr(hardware, 'name', f"ID:{hardware.id}")
        robot_name = hardware.robot.name if hasattr(hardware, 'robot') and hardware.robot else "Unknown Robot"
        site_name = hardware.robot.site.name if hasattr(hardware, 'robot') and hardware.robot and hasattr(hardware.robot, 'site') else "Unknown Site"
        username = user_info['username'] if isinstance(user_info, dict) else user_info
        log_message = f"{username} | {entity_name} | {robot_name} | {site_name} | Changes: {changes_str}"
        logging.info(log_message)
        return True
    return False


# Initialize logging when this module is imported
setup_logging()
# Prevent Uvicorn logs from propagating
logging.getLogger("uvicorn.access").propagate = False
logging.getLogger("uvicorn.error").propagate = False

handler = RotatingFileHandler(
    log_filename, 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3
)

