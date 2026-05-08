import asyncio
import os
import zipfile
import uuid
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from services.font_service import get_font_config, get_google_fonts_url
from services.qr_service import generate_qr_base64
from services.platform_sizes import PLATFORM_SIZES

EXPORTS_DIR = Path("exports")
CARD_TEMPLATES_DIR = Path("card_templates")

jinja_env = Environment(loader=FileSystemLoader(str(CARD_TEMPLATES_DIR)))


async def render_card_to_png(
    template_name: str,
    context: dict,
    width: int,
    height: int,
    output_path: str,
) -> str:
    from playwright.async_api import async_playwright

    template = jinja_env.get_template(f"{template_name}/card.html")
    html_content = template.render(**context)

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page(viewport={"width": width, "height": height})
        await page.set_content(html_content, wait_until="networkidle")
        await page.wait_for_timeout(500)
        await page.screenshot(path=output_path, clip={"x": 0, "y": 0, "width": width, "height": height})
        await browser.close()

    return output_path


async def generate_cards_zip(
    job_id: int,
    template_name: str,
    brand_kit: dict,
    card_data: dict,
    selected_sizes: list,
    language: str,
) -> str:
    font_config = get_font_config(language)
    fonts_url = get_google_fonts_url(language)

    qr_code = ""
    if brand_kit.get("website"):
        qr_code = generate_qr_base64(brand_kit["website"])

    context = {
        "brand": brand_kit,
        "card": card_data,
        "font": font_config,
        "fonts_url": fonts_url,
        "qr_code": qr_code,
        "language": language,
    }

    job_dir = EXPORTS_DIR / f"job_{job_id}_{uuid.uuid4().hex[:6]}"
    job_dir.mkdir(parents=True, exist_ok=True)

    png_files = []
    for size_key in selected_sizes:
        size = PLATFORM_SIZES.get(size_key)
        if not size:
            continue
        ctx = {**context, "size": size, "size_key": size_key}
        filename = f"{size_key}_{size['width']}x{size['height']}.png"
        output_path = str(job_dir / filename)
        await render_card_to_png(template_name, ctx, size["width"], size["height"], output_path)
        png_files.append((filename, output_path))

    zip_path = str(job_dir / f"socialcardcraft_job{job_id}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, path in png_files:
            zf.write(path, filename)

    return zip_path
