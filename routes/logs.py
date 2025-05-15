import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from auth import authenticate_user

router = APIRouter()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

log_file = "logs/hardware_changes.log"

@router.get("/logs", response_class=HTMLResponse)
def get_logs(request: Request, db: Session = Depends(get_db), user: dict = Depends(authenticate_user)):
    try:
        # Check if the log file exists before attempting to read
        if not os.path.exists(log_file):
            return templates.TemplateResponse(
                "logs.html",
                {"request": request, "logs": []}
            )
        
        with open(log_file, "r") as log_file_handle:
            log_lines = log_file_handle.readlines()  # Read all lines into a list
            log_lines.reverse()  # Reverse the list to display the latest logs first
        
        # Parse log entries
        parsed_logs = []
        for log in log_lines:
            try:
                # Parse log entry
                parts = log.strip().split(" - ")
                if len(parts) < 3:
                    continue
                    
                timestamp = parts[0]
                level = parts[1]
                message = parts[2]
                
                # Parse message parts (expected format: "username | hardware | robot | site | Changes: details")
                message_parts = message.split(" | ")
                
                # Handle different log formats
                if "Authenticating user:" in message:
                    parsed_logs.append({
                        "username": "System",
                        "hardware": "",
                        "robot": "",
                        "site": "",
                        "changes": message,
                        "timestamp": timestamp
                    })
                elif "Application started" in message:
                    parsed_logs.append({
                        "username": "System",
                        "hardware": "",
                        "robot": "",
                        "site": "",
                        "changes": "Application started",
                        "timestamp": timestamp
                    })
                elif len(message_parts) >= 4:
                    username = message_parts[0]
                    hardware = message_parts[1] if len(message_parts) > 1 else ""
                    robot = message_parts[2] if len(message_parts) > 2 else ""
                    site = message_parts[3] if len(message_parts) > 3 else ""
                    changes = " | ".join(message_parts[4:]) if len(message_parts) > 4 else ""
                    
                    parsed_logs.append({
                        "username": username,
                        "hardware": hardware,
                        "robot": robot,
                        "site": site,
                        "changes": changes,
                        "timestamp": timestamp
                    })
                else:
                    # Handle other log formats
                    parsed_logs.append({
                        "username": "System",
                        "hardware": "",
                        "robot": "",
                        "site": "",
                        "changes": message,
                        "timestamp": timestamp
                    })
            except Exception as e:
                # Handle parsing errors
                parsed_logs.append({
                    "username": "Error",
                    "hardware": "",
                    "robot": "",
                    "site": "",
                    "changes": f"Error parsing log: {log.strip()}",
                    "timestamp": timestamp if 'timestamp' in locals() else ""
                })
        
        # Return the template response with parsed logs
        return templates.TemplateResponse(
            "logs.html",
            {"request": request, "logs": parsed_logs}
        )
        
    except Exception as e:
        # Return the template with an error message
        return templates.TemplateResponse(
            "logs.html",
            {
                "request": request,
                "logs": [{
                    "username": "Error",
                    "hardware": "",
                    "robot": "",
                    "site": "",
                    "changes": f"An error occurred: {str(e)}",
                    "timestamp": ""
                }]
            }
        )
