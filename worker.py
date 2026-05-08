from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("socialcardcraft", broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "Asia/Kolkata"


@celery_app.task(name="process_export_job")
def process_export_job_task(job_id: int):
    import asyncio
    from models.database import SessionLocal
    from models.export_job import ExportJob
    from models.brand_kit import BrandKit
    from services.renderer import generate_cards_zip
    from services.s3_service import upload_local_file_to_s3
    from datetime import datetime

    db = SessionLocal()
    try:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not job:
            return

        kit = db.query(BrandKit).filter(BrandKit.id == job.brand_kit_id).first()
        job.status = "processing"
        db.commit()

        brand_dict = {
            "name": kit.name,
            "logo_url": kit.logo_url or "",
            "primary_color": kit.primary_color,
            "accent_color": kit.accent_color,
            "instagram": kit.instagram or "",
            "facebook": kit.facebook or "",
            "twitter": kit.twitter or "",
            "linkedin": kit.linkedin or "",
            "youtube": kit.youtube or "",
            "whatsapp": kit.whatsapp or "",
            "phone": kit.phone or "",
            "email": kit.email or "",
            "website": kit.website or "",
        }

        card_dict = {
            "title": job.title or "",
            "subtitle": job.subtitle or "",
            "content": job.content or "",
            "featured_image_url": job.featured_image_url or "",
        }

        zip_path = asyncio.run(generate_cards_zip(
            job_id=job_id,
            template_name=job.card_template,
            brand_kit=brand_dict,
            card_data=card_dict,
            selected_sizes=job.selected_sizes,
            language=job.language,
        ))

        s3_key = f"exports/job_{job_id}.zip"
        zip_url = upload_local_file_to_s3(zip_path, s3_key, "application/zip")

        job.status = "done"
        job.zip_url = zip_url
        job.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()
