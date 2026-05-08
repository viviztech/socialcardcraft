from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import json
import os
from pathlib import Path

from services.font_service import get_font_config, get_google_fonts_url
from services.qr_service import generate_qr_base64

CARD_TEMPLATES_DIR = Path("card_templates")
card_jinja = Environment(loader=FileSystemLoader(str(CARD_TEMPLATES_DIR)))

from models.database import get_db
from models.user import User
from models.brand_kit import BrandKit
from models.export_job import ExportJob
from services.auth_service import get_current_user, reset_daily_exports_if_needed
from services.upload_service import upload_file
from services.platform_sizes import get_sizes_by_platform, PLATFORM_SIZES
from services.font_service import get_all_languages
from services.renderer import generate_cards_zip

router = APIRouter(prefix="/cards", tags=["cards"])
templates = Jinja2Templates(directory="templates")

CARD_TEMPLATES = [
    {"key": "announcement", "label": "Announcement", "icon": "📢", "desc": "News & announcements"},
    {"key": "product_launch", "label": "Product Launch", "icon": "🚀", "desc": "New product reveal"},
    {"key": "quote_card", "label": "Quote Card", "icon": "💬", "desc": "Inspirational quotes"},
    {"key": "event_promo", "label": "Event Promo", "icon": "🎉", "desc": "Events & occasions"},
    {"key": "offer_card", "label": "Offer / Discount", "icon": "🏷️", "desc": "Sale & deals"},
    {"key": "testimonial", "label": "Testimonial", "icon": "⭐", "desc": "Customer reviews"},
    {"key": "blog_teaser", "label": "Blog / Article", "icon": "📝", "desc": "Content teasers"},
]

FREE_DAILY_LIMIT = 3


@router.get("/editor", response_class=HTMLResponse)
async def card_editor(
    request: Request,
    kit_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reset_daily_exports_if_needed(current_user, db)

    brand_kits = db.query(BrandKit).filter(BrandKit.user_id == current_user.id).all()
    selected_kit = None

    if kit_id:
        selected_kit = db.query(BrandKit).filter(
            BrandKit.id == kit_id, BrandKit.user_id == current_user.id
        ).first()

    if not selected_kit and brand_kits:
        selected_kit = next((k for k in brand_kits if k.is_default), brand_kits[0])

    platforms = get_sizes_by_platform()
    languages = get_all_languages()

    return templates.TemplateResponse(
        "cards/editor.html",
        {
            "request": request,
            "user": current_user,
            "brand_kits": brand_kits,
            "selected_kit": selected_kit,
            "card_templates": CARD_TEMPLATES,
            "platforms": platforms,
            "platform_sizes": PLATFORM_SIZES,
            "languages": languages,
            "exports_today": current_user.exports_today,
            "free_limit": FREE_DAILY_LIMIT,
        },
    )


@router.post("/generate")
async def generate_cards(
    request: Request,
    background_tasks: BackgroundTasks,
    brand_kit_id: int = Form(...),
    card_template: str = Form(...),
    title: str = Form(""),
    subtitle: str = Form(""),
    content: str = Form(""),
    language: str = Form("english"),
    selected_sizes: str = Form("[]"),
    featured_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reset_daily_exports_if_needed(current_user, db)

    if current_user.plan == "free" and current_user.exports_today >= FREE_DAILY_LIMIT:
        raise HTTPException(status_code=429, detail="Daily export limit reached. Upgrade to Pro.")

    sizes = json.loads(selected_sizes)
    if not sizes:
        raise HTTPException(status_code=400, detail="Select at least one platform size.")

    kit = db.query(BrandKit).filter(
        BrandKit.id == brand_kit_id, BrandKit.user_id == current_user.id
    ).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found.")

    featured_image_url = None
    if featured_image and featured_image.filename:
        content_bytes = await featured_image.read()
        featured_image_url = upload_file(content_bytes, featured_image.filename, featured_image.content_type, "featured")

    job = ExportJob(
        user_id=current_user.id,
        brand_kit_id=kit.id,
        card_template=card_template,
        title=title,
        subtitle=subtitle,
        content=content,
        featured_image_url=featured_image_url,
        language=language,
        selected_sizes=sizes,
        status="pending",
        total_cards=len(sizes),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    current_user.exports_today += 1
    db.commit()

    background_tasks.add_task(process_export_job, job.id, kit, content, title, subtitle, featured_image_url, language, sizes)

    return RedirectResponse(url=f"/cards/job/{job.id}", status_code=302)


@router.get("/job/{job_id}", response_class=HTMLResponse)
async def job_status(
    request: Request,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(ExportJob).filter(
        ExportJob.id == job_id, ExportJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return templates.TemplateResponse(
        "cards/job_status.html",
        {"request": request, "user": current_user, "job": job},
    )


@router.get("/job/{job_id}/status-json")
async def job_status_json(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(ExportJob).filter(
        ExportJob.id == job_id, ExportJob.user_id == current_user.id
    ).first()
    if not job:
        raise HTTPException(status_code=404)
    return JSONResponse({"status": job.status, "zip_url": job.zip_url, "error": job.error_message})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reset_daily_exports_if_needed(current_user, db)
    recent_jobs = db.query(ExportJob).filter(
        ExportJob.user_id == current_user.id
    ).order_by(ExportJob.created_at.desc()).limit(10).all()
    brand_kits = db.query(BrandKit).filter(BrandKit.user_id == current_user.id).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": current_user,
            "recent_jobs": recent_jobs,
            "brand_kits": brand_kits,
            "exports_today": current_user.exports_today,
            "free_limit": FREE_DAILY_LIMIT,
        },
    )


@router.get("/preview", response_class=HTMLResponse)
async def card_preview(
    request: Request,
    tpl: str = "announcement",
    title: str = "",
    subtitle: str = "",
    content: str = "",
    lang: str = "english",
    kit_id: str = "",
    w: int = 1080,
    h: int = 1080,
    img: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kit_id_int: Optional[int] = int(kit_id) if kit_id and kit_id.isdigit() else None
    font_config = get_font_config(lang)
    fonts_url = get_google_fonts_url(lang)

    brand_dict = {
        "name": "Your Brand",
        "logo_url": "",
        "primary_color": "#6366f1",
        "accent_color": "#f59e0b",
        "instagram": "yourbrand",
        "facebook": "yourbrand",
        "twitter": "yourbrand",
        "linkedin": "yourbrand",
        "youtube": "",
        "whatsapp": "",
        "phone": "+91 99999 99999",
        "email": "hello@yourbrand.com",
        "website": "www.yourbrand.com",
    }

    if kit_id_int:
        from models.brand_kit import BrandKit
        kit = db.query(BrandKit).filter(BrandKit.id == kit_id_int, BrandKit.user_id == current_user.id).first()
        if kit:
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

    qr_code = ""
    if brand_dict.get("website"):
        qr_code = generate_qr_base64(f"https://{brand_dict['website']}")

    template_name = tpl if (CARD_TEMPLATES_DIR / tpl / "card.html").exists() else "announcement"

    try:
        tmpl = card_jinja.get_template(f"{template_name}/card.html")
        html = tmpl.render(
            brand=brand_dict,
            card={"title": title, "subtitle": subtitle, "content": content, "featured_image_url": img},
            font=font_config,
            fonts_url=fonts_url,
            qr_code=qr_code,
            language=lang,
            size={"width": w, "height": h, "label": f"{w}×{h}"},
            size_key="preview",
        )
        return HTMLResponse(content=html)
    except Exception as e:
        return HTMLResponse(content=f"<html><body style='background:#111;color:#f87171;padding:20px;font-family:monospace'>Preview error: {e}</body></html>")


async def process_export_job(
    job_id: int,
    kit: BrandKit,
    card_content: str,
    title: str,
    subtitle: str,
    featured_image_url: Optional[str],
    language: str,
    selected_sizes: list,
):
    from models.database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(ExportJob).filter(ExportJob.id == job_id).first()
        if not job:
            return

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
            "title": title,
            "subtitle": subtitle,
            "content": card_content,
            "featured_image_url": featured_image_url or "",
        }

        zip_path = await generate_cards_zip(
            job_id=job_id,
            template_name=job.card_template,
            brand_kit=brand_dict,
            card_data=card_dict,
            selected_sizes=selected_sizes,
            language=language,
        )

        # Try S3, serve locally if not configured
        try:
            from services.s3_service import upload_local_file_to_s3
            aws_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            if aws_key and not aws_key.startswith("REPLACE") and not aws_key.startswith("your"):
                s3_key = f"exports/job_{job_id}.zip"
                zip_url = upload_local_file_to_s3(zip_path, s3_key, "application/zip")
            else:
                raise ValueError("S3 not configured")
        except Exception:
            zip_url = f"/exports/{zip_path.split('exports/')[-1]}" if "exports/" in zip_path else f"/exports/job_{job_id}.zip"

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
