from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand_kit_id = Column(Integer, ForeignKey("brand_kits.id"), nullable=True)

    # Card Content
    card_template = Column(String(50), nullable=False)   # announcement, product_launch, etc.
    title = Column(String(200), nullable=True)
    subtitle = Column(String(300), nullable=True)
    content = Column(Text, nullable=True)
    featured_image_url = Column(Text, nullable=True)
    language = Column(String(30), default="english")

    # Selected platforms/sizes as JSON list
    selected_sizes = Column(JSON, default=list)

    # Job state
    status = Column(String(20), default="pending")  # pending, processing, done, failed
    zip_url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    total_cards = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="export_jobs")
    brand_kit = relationship("BrandKit", back_populates="export_jobs")
