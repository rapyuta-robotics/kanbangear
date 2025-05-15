import os
from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import FastAPI, status


app = FastAPI()
security = HTTPBasic()


from routes import site, robot, logs  
from database import engine, Base 
import logging
import logging_utils  
import config 
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi_limiter import FastAPILimiter  # <-- Add this import here
import redis.asyncio as redis



Instrumentator().instrument(app).expose(app)
app.add_middleware(GZipMiddleware)

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_db():
    # Create tables in the database
    Base.metadata.create_all(bind=engine)
    
    # Set up Redis connection for the rate limiter
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_connection = redis.from_url(f"redis://{redis_host}")
    await FastAPILimiter.init(redis_connection)
    
    logging.info("Application started")



app.include_router(site.router)   # Register site-related routes
app.include_router(robot.router)  # Register robot & hardware routes
app.include_router(logs.router)  # Register logs route

# Define a health check response model
class HealthCheck(BaseModel):
    status: str = "OK"

# Add health check endpoint
@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    Perform a Health Check
    
    Endpoint to verify the application is running correctly.
    Used by Docker and other services to monitor application health.
    """
    return HealthCheck(status="OK")