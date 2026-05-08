from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models.user import User
from services.auth_service import get_current_user

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect(current_user: User = Depends(get_current_user)):
    return RedirectResponse(url="/cards/dashboard", status_code=302)
