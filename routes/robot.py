import logging
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Robot, Hardware, Site
from schemas import RobotCreate, HardwareCreate
from auth import authenticate_user
from pydantic import BaseModel
from schemas import RobotResponse
from logging_utils import log_hardware_changes
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

# Get list of robots
@router.get("/robots", response_model=List[RobotResponse])
def get_robots(db: Session = Depends(get_db)):
    return db.query(Robot).all()

# Request models
class UpdateReplacementCountRequest(BaseModel):
    hardware_id: int
    replacement_count: int

class UpdateRepairCountRequest(BaseModel):
    hardware_id: int
    repair_count: int

class UpdateStatusRequest(BaseModel):
    hardware_id: int
    status: str

class UpdateHardwareRequest(BaseModel):
    hardware_id: int
    replacement_count: Optional[int] = None
    repair_count: Optional[int] = None
    status: Optional[str] = None
    comments: Optional[str] = None  # <-- Add this line

@router.post("/update_hardware")
def update_hardware(
    data: UpdateHardwareRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(authenticate_user),
):
    hardware = db.query(Hardware).filter(Hardware.id == data.hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")

    old_values = {
        'replacement_count': hardware.replacement_count,
        'repair_count': hardware.repair_count,
        'status': hardware.status,
        'comments': hardware.comments  # Track comments changes
    }
    new_values = {}
    if data.replacement_count is not None:
        new_values['replacement_count'] = data.replacement_count
        hardware.replacement_count = data.replacement_count
    if data.repair_count is not None:
        new_values['repair_count'] = data.repair_count
        hardware.repair_count = data.repair_count
    if data.status is not None:
        new_values['status'] = data.status
        hardware.status = data.status
    if data.comments is not None:  # Handle comments
        hardware.comments = data.comments
        new_values['comments'] = data.comments

    db.commit()

    # Pass reason to logger
    if data.comments:
        new_values['comments'] = data.comments

    changes_logged = log_hardware_changes(
        hardware=hardware,
        old_values=old_values,
        new_values=new_values,
        user_info=current_user
    )

    if changes_logged:
        return {"message": "Hardware updated successfully"}
    return {"message": "No changes detected"}

# Form-based update endpoint
@router.post("/update_hardware_form")
async def update_hardware_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(authenticate_user)
):
    form_data = await request.form()
    hardware_id = int(form_data.get("hardware_id"))
    
    hardware = db.query(Hardware).filter(Hardware.id == hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    
    # Store old values
    old_values = {
        'replacement_count': hardware.replacement_count,
        'repair_count': hardware.repair_count,
        'status': hardware.status,
    }
    
    # Process form data and update hardware
    new_values = {}
    
    if "replacement_count" in form_data:
        new_count = int(form_data.get("replacement_count"))
        if new_count != hardware.replacement_count:
            new_values['replacement_count'] = new_count
            hardware.replacement_count = new_count
    
    if "repair_count" in form_data:
        new_count = int(form_data.get("repair_count"))
        if new_count != hardware.repair_count:
            new_values['repair_count'] = new_count
            hardware.repair_count = new_count
    
    if "status" in form_data:
        new_status = form_data.get("status")
        if new_status != hardware.status:
            new_values['status'] = new_status
            hardware.status = new_status
    if "comments" in form_data:
        new_comments = form_data.get("comments")
        if new_comments != hardware.comments:
            new_values['comments'] = new_comments
            hardware.comments = new_comments
    
    # Commit changes to database
    db.commit()
    
    # Log all changes in one entry
    changes_logged = log_hardware_changes(
        hardware=hardware,
        old_values=old_values,
        new_values=new_values,
        user_info=current_user
    )
    
    if changes_logged:
        return {"message": "Hardware updated successfully"}
    return {"message": "No changes detected"}

# Keep the individual update endpoints for backward compatibility
# Update replacement count
@router.post("/update_replacement_count")
def update_replacement_count(
    data: UpdateReplacementCountRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(authenticate_user),
):
    hardware = db.query(Hardware).filter(Hardware.id == data.hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    
    # Store old values
    old_values = {
        'replacement_count': hardware.replacement_count
    }
    
    # New values
    new_values = {
        'replacement_count': data.replacement_count
    }
    
    # Update hardware
    hardware.replacement_count = data.replacement_count
    db.commit()
    
    # Log changes
    changes_logged = log_hardware_changes(
        hardware=hardware,
        old_values=old_values,
        new_values=new_values,
        user_info=current_user
    )
    
    if changes_logged:
        return {"message": "Replacement count updated successfully"}
    return {"message": "No changes detected"}

# Update status
@router.post("/update_status")
def update_status(
    data: UpdateStatusRequest, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(authenticate_user)
):
    hardware = db.query(Hardware).filter(Hardware.id == data.hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    
    # Store old values
    old_values = {
        'status': hardware.status
    }
    
    # New values
    new_values = {
        'status': data.status
    }
    
    # Update hardware
    hardware.status = data.status
    db.commit()
    
    # Log changes
    changes_logged = log_hardware_changes(
        hardware=hardware,
        old_values=old_values,
        new_values=new_values,
        user_info=current_user
    )
    
    if changes_logged:
        return {"message": "Status updated successfully"}
    return {"message": "No changes detected"}

# Update repair count
@router.post("/update_repair_count")
def update_repair_count(
    data: UpdateRepairCountRequest, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(authenticate_user)
):
    hardware = db.query(Hardware).filter(Hardware.id == data.hardware_id).first()
    if not hardware:
        raise HTTPException(status_code=404, detail="Hardware not found")
    
    # Store old values
    old_values = {
        'repair_count': hardware.repair_count
    }
    
    # New values
    new_values = {
        'repair_count': data.repair_count
    }
    
    # Update hardware
    hardware.repair_count = data.repair_count
    db.commit()
    
    # Log changes
    changes_logged = log_hardware_changes(
        hardware=hardware,
        old_values=old_values,
        new_values=new_values,
        user_info=current_user
    )
    
    if changes_logged:
        return {"message": "Repair count updated successfully"}
    return {"message": "No changes detected"}

# Create a new robot
@router.post("/robot/")
def create_robot(
    robot: RobotCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(authenticate_user)
):
    db_robot = db.query(Robot).filter(Robot.name == robot.name, Robot.site_id == robot.site_id).first()
    if db_robot:
        raise HTTPException(status_code=400, detail="Robot already exists")
    
    site = db.query(Site).filter(Site.id == robot.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    new_robot = Robot(name=robot.name, site_id=robot.site_id)
    db.add(new_robot)
    db.commit()
    db.refresh(new_robot)
    
    logging.info(f"{current_user['username']} | {new_robot.name} | {site.name} | Changes: Created new robot")
    
    return {"message": "Robot created successfully", "robot_id": new_robot.id}

# Create a new hardware item
@router.post("/hardware/")
def create_hardware(
    hardware: HardwareCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(authenticate_user)
):
    db_hardware = db.query(Hardware).filter(Hardware.name == hardware.name, Hardware.robot_id == hardware.robot_id).first()
    if db_hardware:
        raise HTTPException(status_code=400, detail="Hardware already exists")
    
    robot = db.query(Robot).filter(Robot.id == hardware.robot_id).first()
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    new_hardware = Hardware(
        name=hardware.name, 
        type=hardware.type, 
        robot_id=hardware.robot_id,
        status=hardware.status,
        replacement_count=hardware.replacement_count,
        repair_count=hardware.repair_count,
        comments=hardware.comments
    )
    db.add(new_hardware)
    db.commit()
    db.refresh(new_hardware)
    
    logging.info(f"{current_user['username']} | {new_hardware.name} | {robot.name} | {robot.site.name} | Changes: Created new hardware")
    
    return {"message": "Hardware created successfully", "hardware_id": new_hardware.id}
