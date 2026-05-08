from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, List

from models.user import User
from services.auth_service import get_current_user
from services import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


# ─── Request schemas ──────────────────────────────────────────────────────────

class ContentRequest(BaseModel):
    topic: str
    brand_name: str = ""
    template: str = "announcement"
    language: str = "english"
    tone: str = "professional"


class RecommendRequest(BaseModel):
    description: str
    brand_name: str = ""


class CaptionRequest(BaseModel):
    title: str = ""
    subtitle: str = ""
    content: str = ""
    brand_name: str = ""
    template: str = "announcement"
    language: str = "english"
    platforms: Optional[List[str]] = None


class ImageRequest(BaseModel):
    prompt: str
    template: str = "announcement"
    brand_name: str = ""
    width: int = 1080
    height: int = 1080


class EnhancePromptRequest(BaseModel):
    prompt: str
    template: str = "announcement"
    brand_name: str = ""


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/generate-content")
async def generate_content(
    req: ContentRequest,
    current_user: User = Depends(get_current_user),
):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")
    result = await ai_service.generate_card_content(
        topic=req.topic,
        brand_name=req.brand_name,
        template=req.template,
        language=req.language,
        tone=req.tone,
    )
    return JSONResponse(result)


@router.post("/recommend-template")
async def recommend_template(
    req: RecommendRequest,
    current_user: User = Depends(get_current_user),
):
    if not req.description.strip():
        raise HTTPException(status_code=400, detail="Description is required.")
    result = await ai_service.recommend_template(
        description=req.description,
        brand_name=req.brand_name,
    )
    return JSONResponse(result)


@router.post("/generate-captions")
async def generate_captions(
    req: CaptionRequest,
    current_user: User = Depends(get_current_user),
):
    result = await ai_service.generate_captions(
        title=req.title,
        subtitle=req.subtitle,
        content=req.content,
        brand_name=req.brand_name,
        template=req.template,
        language=req.language,
        platforms=req.platforms,
    )
    return JSONResponse(result)


@router.post("/generate-image")
async def generate_image(
    req: ImageRequest,
    current_user: User = Depends(get_current_user),
):
    enhanced_prompt = await ai_service.enhance_image_prompt(
        user_prompt=req.prompt,
        template=req.template,
        brand_name=req.brand_name,
    )
    img_bytes = await ai_service.generate_image(
        prompt=enhanced_prompt,
        width=req.width,
        height=req.height,
    )
    if img_bytes:
        from services.s3_service import upload_file_to_s3
        url = upload_file_to_s3(img_bytes, "ai_generated.png", "image/png", "ai-images")
        return JSONResponse({"url": url, "provider": ai_service.IMAGE_GEN_PROVIDER, "enhanced_prompt": enhanced_prompt})
    return JSONResponse({"url": None, "provider": "none", "enhanced_prompt": enhanced_prompt, "message": "No image provider configured. Add STABILITY_API_KEY or REPLICATE_API_TOKEN to .env"})


@router.post("/enhance-prompt")
async def enhance_prompt(
    req: EnhancePromptRequest,
    current_user: User = Depends(get_current_user),
):
    enhanced = await ai_service.enhance_image_prompt(
        user_prompt=req.prompt,
        template=req.template,
        brand_name=req.brand_name,
    )
    return JSONResponse({"enhanced_prompt": enhanced})


@router.get("/provider-status")
async def provider_status(current_user: User = Depends(get_current_user)):
    provider = ai_service._active_provider()
    return JSONResponse({
        "active_provider": provider,
        "claude": bool(ai_service.ANTHROPIC_API_KEY and ai_service.ANTHROPIC_API_KEY.startswith("sk-ant")),
        "openai": bool(ai_service.OPENAI_API_KEY and ai_service.OPENAI_API_KEY.startswith("sk-")),
        "ollama": provider == "ollama",
        "image_provider": ai_service.IMAGE_GEN_PROVIDER,
    })
