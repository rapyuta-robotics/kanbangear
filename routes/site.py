import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas import SiteCreate
from auth import check_admin_role
from fastapi.responses import HTMLResponse, StreamingResponse
from models import Site, Robot, Hardware
from auth_helpers import authenticate_user
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import joinedload
import re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Create a new site (unchanged)
@router.post("/site/")
def create_site(site: SiteCreate, db: Session = Depends(get_db), current_user: dict = Depends(check_admin_role)):
    db_site = db.query(Site).filter(Site.name == site.name).first()
    if db_site:
        raise HTTPException(status_code=400, detail="Site already exists")
    new_site = Site(name=site.name)
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    logging.info(f"{current_user['username']} | Site | {new_site.name} | Changes: Created new site")
    return {"message": "Site created successfully", "site_id": new_site.id}

# Site details page (now uses Jinja2)
@router.get("/site/{site_name}", response_class=HTMLResponse)
def get_site_details(
    request: Request,
    site_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(authenticate_user)
):
    site = db.query(Site).options(joinedload(Site.robots).joinedload(Robot.hardware)).filter(Site.name.ilike(site_name)).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # Sort robots naturally, e.g., AMR1, AMR2, AMR10
    def natural_key(robot):
        match = re.search(r'\d+', robot.name)
        return int(match.group()) if match else float('inf')
    
    site.robots.sort(key=natural_key)
    return templates.TemplateResponse(
        "site.html",
        {
            "request": request,
            "site": site,
            "site_name": site_name
        }
    )

# CSV download (unchanged)
@router.get("/download_csv/{site_name}")
def download_csv(site_name: str, db: Session = Depends(get_db)):
    site = db.query(Site).options(joinedload(Site.robots).joinedload(Robot.hardware)).filter(Site.name.ilike(site_name)).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    def generate_csv():
        yield "Site Name,Robot Name,Hardware Name,Type,Status,Replacement Count,Repair Count,Comments\n"
        for robot in site.robots:
            for hw in robot.hardware:
                yield f"{site.name},{robot.name},{hw.name},{hw.type},{hw.status},{hw.replacement_count},{hw.repair_count},{hw.comments}\n"
    return StreamingResponse(generate_csv(), media_type="text/csv", headers={"Content-Disposition": f"attachment; filename={site_name}_hardware.csv"})

@router.get("/sites", response_class=HTMLResponse)
def list_all_sites(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(authenticate_user)
):
    sites = db.query(Site).all()
    return templates.TemplateResponse(
        "sites_list.html",
        {
            "request": request,
            "sites": sites
        }
    )
