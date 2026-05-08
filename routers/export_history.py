from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models.database import get_db
from models.user import User
from models.export_job import ExportJob
from services.auth_service import get_current_user

router = APIRouter(prefix="/history", tags=["history"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def export_history(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    jobs = db.query(ExportJob).filter(
        ExportJob.user_id == current_user.id
    ).order_by(ExportJob.created_at.desc()).all()
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "user": current_user, "jobs": jobs},
    )
