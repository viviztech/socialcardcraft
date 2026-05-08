from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from sqlalchemy.exc import OperationalError, IntegrityError
import os
from dotenv import load_dotenv

from models.database import Base, engine
from routers import auth, brand_kit, cards, admin, export_history, dashboard, ai

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception as e:
        print(f"[startup] DB init warning: {e}")
    await create_default_admin()
    yield


async def create_default_admin():
    from models.database import SessionLocal
    from models.user import User
    from services.auth_service import hash_password

    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@socialcardcraft.com")
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            admin_user = User(
                name="Admin",
                email=admin_email,
                hashed_password=hash_password(os.getenv("ADMIN_PASSWORD", "Admin@1234")),
                is_admin=True,
                plan="pro",
            )
            db.add(admin_user)
            db.commit()
    except (IntegrityError, OperationalError):
        db.rollback()
    except Exception as e:
        print(f"[startup] Admin create warning: {e}")
        db.rollback()
    finally:
        db.close()


app = FastAPI(title="SocialCardCraft", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(brand_kit.router)
app.include_router(cards.router)
app.include_router(admin.router)
app.include_router(export_history.router)
app.include_router(dashboard.router)
app.include_router(ai.router)


@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/dashboard")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8013))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
