from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from models.database import get_db
from models.user import User
from models.brand_kit import BrandKit
from models.export_job import ExportJob
from services.auth_service import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    total_users = db.query(func.count(User.id)).scalar()
    total_exports = db.query(func.count(ExportJob.id)).scalar()
    pro_users = db.query(func.count(User.id)).filter(User.plan == "pro").scalar()
    today = datetime.utcnow().date()
    exports_today = db.query(func.count(ExportJob.id)).filter(
        func.date(ExportJob.created_at) == today
    ).scalar()
    recent_jobs = db.query(ExportJob).order_by(ExportJob.created_at.desc()).limit(20).all()
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(10).all()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "user": admin,
            "admin": admin,
            "total_users": total_users,
            "total_exports": total_exports,
            "pro_users": pro_users,
            "exports_today": exports_today,
            "recent_jobs": recent_jobs,
            "recent_users": recent_users,
        },
    )


@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin/users.html",
        {"request": request, "user": admin, "admin": admin, "users": users},
    )


@router.post("/users/{user_id}/toggle-plan")
async def toggle_user_plan(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.plan = "pro" if user.plan == "free" else "free"
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user and not user.is_admin:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/jobs", response_class=HTMLResponse)
async def admin_jobs(
    request: Request,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    jobs = db.query(ExportJob).order_by(ExportJob.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "admin/jobs.html",
        {"request": request, "user": admin, "admin": admin, "jobs": jobs},
    )
