from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from models.user import User
from models.brand_kit import BrandKit
from services.auth_service import get_current_user
from services.upload_service import upload_file
from services.font_service import get_all_languages

router = APIRouter(prefix="/brand-kit", tags=["brand-kit"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def brand_kit_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kits = db.query(BrandKit).filter(BrandKit.user_id == current_user.id).all()
    return templates.TemplateResponse(
        "brand_kit/list.html",
        {"request": request, "user": current_user, "kits": kits},
    )


@router.get("/new", response_class=HTMLResponse)
async def brand_kit_new(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    languages = get_all_languages()
    return templates.TemplateResponse(
        "brand_kit/form.html",
        {"request": request, "user": current_user, "kit": None, "languages": languages},
    )


@router.post("/new")
async def brand_kit_create(
    request: Request,
    name: str = Form("My Brand"),
    primary_color: str = Form("#6366f1"),
    accent_color: str = Form("#f59e0b"),
    font_language: str = Form("english"),
    instagram: str = Form(""),
    facebook: str = Form(""),
    twitter: str = Form(""),
    linkedin: str = Form(""),
    youtube: str = Form(""),
    whatsapp: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    logo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logo_url = None
    if logo and logo.filename:
        content = await logo.read()
        logo_url = upload_file(content, logo.filename, logo.content_type, "logos")

    kit = BrandKit(
        user_id=current_user.id,
        name=name,
        primary_color=primary_color,
        accent_color=accent_color,
        font_language=font_language,
        logo_url=logo_url,
        instagram=instagram or None,
        facebook=facebook or None,
        twitter=twitter or None,
        linkedin=linkedin or None,
        youtube=youtube or None,
        whatsapp=whatsapp or None,
        phone=phone or None,
        email=email or None,
        website=website or None,
    )

    existing_default = db.query(BrandKit).filter(
        BrandKit.user_id == current_user.id, BrandKit.is_default == True
    ).first()
    if not existing_default:
        kit.is_default = True

    db.add(kit)
    db.commit()
    return RedirectResponse(url="/brand-kit/", status_code=302)


@router.get("/{kit_id}/edit", response_class=HTMLResponse)
async def brand_kit_edit(
    request: Request,
    kit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kit = db.query(BrandKit).filter(BrandKit.id == kit_id, BrandKit.user_id == current_user.id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    languages = get_all_languages()
    return templates.TemplateResponse(
        "brand_kit/form.html",
        {"request": request, "user": current_user, "kit": kit, "languages": languages},
    )


@router.post("/{kit_id}/edit")
async def brand_kit_update(
    request: Request,
    kit_id: int,
    name: str = Form("My Brand"),
    primary_color: str = Form("#6366f1"),
    accent_color: str = Form("#f59e0b"),
    font_language: str = Form("english"),
    instagram: str = Form(""),
    facebook: str = Form(""),
    twitter: str = Form(""),
    linkedin: str = Form(""),
    youtube: str = Form(""),
    whatsapp: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    logo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kit = db.query(BrandKit).filter(BrandKit.id == kit_id, BrandKit.user_id == current_user.id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")

    if logo and logo.filename:
        content = await logo.read()
        kit.logo_url = upload_file_to_s3(content, logo.filename, logo.content_type, "logos")

    kit.name = name
    kit.primary_color = primary_color
    kit.accent_color = accent_color
    kit.font_language = font_language
    kit.instagram = instagram or None
    kit.facebook = facebook or None
    kit.twitter = twitter or None
    kit.linkedin = linkedin or None
    kit.youtube = youtube or None
    kit.whatsapp = whatsapp or None
    kit.phone = phone or None
    kit.email = email or None
    kit.website = website or None

    db.commit()
    return RedirectResponse(url="/brand-kit/", status_code=302)


@router.post("/{kit_id}/set-default")
async def set_default_kit(
    kit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(BrandKit).filter(BrandKit.user_id == current_user.id).update({"is_default": False})
    kit = db.query(BrandKit).filter(BrandKit.id == kit_id, BrandKit.user_id == current_user.id).first()
    if kit:
        kit.is_default = True
        db.commit()
    return RedirectResponse(url="/brand-kit/", status_code=302)


@router.post("/{kit_id}/delete")
async def delete_kit(
    kit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kit = db.query(BrandKit).filter(BrandKit.id == kit_id, BrandKit.user_id == current_user.id).first()
    if kit:
        db.delete(kit)
        db.commit()
    return RedirectResponse(url="/brand-kit/", status_code=302)
