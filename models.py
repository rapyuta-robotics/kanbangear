import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Database Models
class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    robots = relationship("Robot", back_populates="site", cascade="all, delete-orphan")

class Robot(Base):
    __tablename__ = "robots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    site = relationship("Site", back_populates="robots")
    hardware = relationship("Hardware", back_populates="robot", cascade="all, delete-orphan")

class Hardware(Base):
    __tablename__ = "hardware"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="Active")
    replacement_count = Column(Integer, default=0)
    repair_count = Column(Integer, default=0)
    comments = Column(Text, default="")  # New field for comment
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    robot = relationship("Robot", back_populates="hardware")

