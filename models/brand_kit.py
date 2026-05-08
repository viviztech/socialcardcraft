from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class BrandKit(Base):
    __tablename__ = "brand_kits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), default="My Brand")
    is_default = Column(Boolean, default=False)

    # Brand Identity
    logo_url = Column(Text, nullable=True)
    primary_color = Column(String(10), default="#6366f1")
    accent_color = Column(String(10), default="#f59e0b")
    font_language = Column(String(30), default="english")

    # Social Handles
    instagram = Column(String(100), nullable=True)
    facebook = Column(String(100), nullable=True)
    twitter = Column(String(100), nullable=True)
    linkedin = Column(String(100), nullable=True)
    youtube = Column(String(100), nullable=True)
    whatsapp = Column(String(20), nullable=True)

    # Contact
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="brand_kits")
    export_jobs = relationship("ExportJob", back_populates="brand_kit")
