from pydantic import BaseModel

# Pydantic Models for Request Validation
class SiteCreate(BaseModel):
    name: str

class RobotCreate(BaseModel):
    name: str
    site_id: int

class HardwareCreate(BaseModel):
    name: str
    type: str
    robot_id: int
    status: str = "Active"
    replacement_count: int = 0
    repair_count: int = 0
    comments: str = ""

class RobotResponse(BaseModel):
    id: int
    name: str
    site_id: int

    class Config:
        from_attributes = True

