"""
AI Service — flexible model router.
Priority: Claude API → OpenAI API → Ollama local → rule-based fallback.
"""
import os
import json
import re
import httpx
from typing import Optional

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")


def _active_provider() -> str:
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.startswith("sk-ant"):
        return "claude"
    if OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"):
        return "openai"
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            return "ollama"
    except Exception:
        pass
    return "fallback"


async def _call_claude(prompt: str, system: str = "") -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system or "You are a creative social media content expert.",
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


async def _call_openai(prompt: str, system: str = "") -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system or "You are a creative social media content expert."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 1024,
                "temperature": 0.8,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_ollama(prompt: str, system: str = "") -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system}\n\n{prompt}" if system else prompt,
                "stream": False,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["response"]


async def _llm(prompt: str, system: str = "") -> str:
    provider = _active_provider()
    if provider == "claude":
        return await _call_claude(prompt, system)
    elif provider == "openai":
        return await _call_openai(prompt, system)
    elif provider == "ollama":
        return await _call_ollama(prompt, system)
    raise RuntimeError("no_provider")


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group())
    return json.loads(text)


# ─── 1. CONTENT WRITER ───────────────────────────────────────────────────────

LANGUAGE_INSTRUCTIONS = {
    "hindi": "Write entirely in Hindi (Devanagari script).",
    "tamil": "Write entirely in Tamil script.",
    "telugu": "Write entirely in Telugu script.",
    "kannada": "Write entirely in Kannada script.",
    "malayalam": "Write entirely in Malayalam script.",
    "bengali": "Write entirely in Bengali script.",
    "marathi": "Write entirely in Marathi (Devanagari script).",
    "gujarati": "Write entirely in Gujarati script.",
    "punjabi": "Write entirely in Punjabi (Gurmukhi script).",
    "odia": "Write entirely in Odia script.",
    "urdu": "Write entirely in Urdu (Nastaliq script), right-to-left.",
    "assamese": "Write entirely in Assamese script.",
    "sanskrit": "Write entirely in Sanskrit (Devanagari script).",
    "english": "Write in clear, engaging English.",
}

TONE_INSTRUCTIONS = {
    "professional": "Use a professional, authoritative tone.",
    "casual": "Use a friendly, conversational tone.",
    "festive": "Use an enthusiastic, celebratory tone with energy.",
    "urgent": "Use urgency-driven language with a strong call to action.",
    "inspirational": "Use uplifting, motivational language.",
}

TEMPLATE_CONTEXT = {
    "announcement": "This is an announcement card. Create content that informs and grabs attention.",
    "product_launch": "This is a product launch card. Build excitement and highlight benefits.",
    "quote_card": "This is a quote card. Create a powerful, memorable quote or statement.",
    "event_promo": "This is an event promotion card. Create excitement and urgency to attend.",
    "offer_card": "This is a discount/offer card. Highlight the deal and create urgency.",
    "testimonial": "This is a testimonial card. The title should be the customer quote (max 15 words), subtitle is customer name, content is their role/company.",
    "blog_teaser": "This is a blog article teaser. Create a compelling headline and excerpt.",
}

FALLBACK_CONTENT = {
    "announcement": {"title": "Big News Is Here!", "subtitle": "We have something exciting to share with you", "content": "Stay tuned for more updates from our team. Follow us on all social platforms to never miss out."},
    "product_launch": {"title": "Introducing Our New Product", "subtitle": "Innovation that changes everything", "content": "Experience the future today. Crafted with precision, designed for you."},
    "quote_card": {"title": "Success is not final, failure is not fatal — it is the courage to continue that counts.", "subtitle": "Winston Churchill", "content": ""},
    "event_promo": {"title": "Join Us for an Unforgettable Event", "subtitle": "Date & Venue TBA — Register Now", "content": "Limited seats available. Reserve your spot before it's too late!"},
    "offer_card": {"title": "Exclusive Deal Just for You", "subtitle": "50%", "content": "Limited time offer. Shop now and save big on your favorite products."},
    "testimonial": {"title": "This product completely changed how I work. Highly recommended!", "subtitle": "Happy Customer", "content": "Verified Buyer"},
    "blog_teaser": {"title": "5 Things You Need to Know About This Topic", "subtitle": "A must-read for everyone", "content": "Discover insights that will transform your perspective. Read the full article on our website."},
}


async def generate_card_content(
    topic: str,
    brand_name: str,
    template: str,
    language: str = "english",
    tone: str = "professional",
) -> dict:
    lang_instr = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["english"])
    tone_instr = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["professional"])
    tpl_context = TEMPLATE_CONTEXT.get(template, "Create engaging social media card content.")

    system = (
        "You are an expert social media copywriter specializing in Indian brands. "
        f"{lang_instr} {tone_instr} "
        "Always respond with valid JSON only, no explanation."
    )

    prompt = f"""{tpl_context}

Brand: {brand_name}
Topic / Product / Event: {topic}

Generate card copy and return ONLY this JSON:
{{
  "title": "...",
  "subtitle": "...",
  "content": "..."
}}

Rules:
- title: max 80 characters, bold headline
- subtitle: max 120 characters, supporting line
- content: max 200 characters, body copy or CTA
- All text in the requested language
- No placeholder text"""

    try:
        raw = await _llm(prompt, system)
        data = _extract_json(raw)
        return {
            "title": str(data.get("title", ""))[:120],
            "subtitle": str(data.get("subtitle", ""))[:160],
            "content": str(data.get("content", ""))[:300],
            "provider": _active_provider(),
        }
    except Exception:
        fb = FALLBACK_CONTENT.get(template, FALLBACK_CONTENT["announcement"])
        return {**fb, "provider": "fallback"}


# ─── 2. TEMPLATE RECOMMENDER ─────────────────────────────────────────────────

TEMPLATE_DESCRIPTIONS = {
    "announcement": "News, updates, important information",
    "product_launch": "New product, service, or feature reveal",
    "quote_card": "Quotes, tips, motivational messages",
    "event_promo": "Events, webinars, meetups, festivals",
    "offer_card": "Sales, discounts, coupons, deals",
    "testimonial": "Customer reviews, success stories",
    "blog_teaser": "Blog posts, articles, content teasers",
}

COLOR_PALETTES = {
    "vibrant": {"primary_color": "#6366f1", "accent_color": "#f59e0b"},
    "professional": {"primary_color": "#1e40af", "accent_color": "#0ea5e9"},
    "festive": {"primary_color": "#dc2626", "accent_color": "#f97316"},
    "nature": {"primary_color": "#16a34a", "accent_color": "#84cc16"},
    "luxury": {"primary_color": "#7c3aed", "accent_color": "#f59e0b"},
    "minimal": {"primary_color": "#1f2937", "accent_color": "#6b7280"},
    "warm": {"primary_color": "#b45309", "accent_color": "#f59e0b"},
}

FALLBACK_RECOMMENDATIONS = {
    "launch": {"template": "product_launch", "palette": "vibrant", "reason": "Product launches need bold, exciting visuals"},
    "sale": {"template": "offer_card", "palette": "festive", "reason": "Offers need urgent, attention-grabbing colors"},
    "event": {"template": "event_promo", "palette": "festive", "reason": "Events need energy and excitement"},
    "review": {"template": "testimonial", "palette": "professional", "reason": "Testimonials need credibility and trust"},
    "blog": {"template": "blog_teaser", "palette": "minimal", "reason": "Blog teasers need clean, readable design"},
    "quote": {"template": "quote_card", "palette": "luxury", "reason": "Quote cards need elegant, memorable presentation"},
}


async def recommend_template(description: str, brand_name: str = "") -> dict:
    templates_list = "\n".join([f"- {k}: {v}" for k, v in TEMPLATE_DESCRIPTIONS.items()])
    palettes_list = "\n".join([f"- {k}: primary={v['primary']}, accent={v['accent']}" for k, v in COLOR_PALETTES.items()])

    system = "You are a social media design expert. Respond with valid JSON only."
    prompt = f"""A brand wants to create a social media card. Based on their description, recommend the best template and color palette.

Brand: {brand_name or 'Unknown'}
Description: {description}

Available templates:
{templates_list}

Available palettes:
{palettes_list}

Return ONLY this JSON:
{{
  "template": "<template_key>",
  "palette": "<palette_key>",
  "primary_color": "<hex>",
  "accent_color": "<hex>",
  "reason": "<one sentence why>",
  "suggested_topic": "<refined topic for content generation>"
}}"""

    try:
        raw = await _llm(prompt, system)
        data = _extract_json(raw)
        palette_key = data.get("palette", "vibrant")
        palette = COLOR_PALETTES.get(palette_key, COLOR_PALETTES["vibrant"])
        return {
            "template": data.get("template", "announcement"),
            "palette": palette_key,
            "primary_color": data.get("primary_color", palette["primary"]),
            "accent_color": data.get("accent_color", palette["accent"]),
            "reason": data.get("reason", ""),
            "suggested_topic": data.get("suggested_topic", description),
            "provider": _active_provider(),
        }
    except Exception:
        desc_lower = description.lower()
        for kw, rec in FALLBACK_RECOMMENDATIONS.items():
            if kw in desc_lower:
                palette = COLOR_PALETTES[rec["palette"]]
                return {**rec, **palette, "suggested_topic": description, "provider": "fallback"}
        palette = COLOR_PALETTES["vibrant"]
        return {
            "template": "announcement", "palette": "vibrant",
            "primary_color": palette["primary"], "accent_color": palette["accent"],
            "reason": "Announcement is a versatile all-purpose template.",
            "suggested_topic": description, "provider": "fallback",
        }


# ─── 3. CAPTION & HASHTAG GENERATOR ─────────────────────────────────────────

PLATFORM_CAPTION_STYLES = {
    "instagram": "Instagram: casual, emoji-rich, 3-5 lines, strong hook. Max 200 chars.",
    "facebook": "Facebook: conversational, slightly longer, community-focused. Max 250 chars.",
    "twitter": "X/Twitter: punchy, max 250 chars, 2-3 hashtags inline.",
    "linkedin": "LinkedIn: professional, value-focused, no excessive emojis. Max 300 chars.",
    "whatsapp": "WhatsApp: friendly, personal, short. Max 150 chars.",
}


async def generate_captions(
    title: str,
    subtitle: str,
    content: str,
    brand_name: str,
    template: str,
    language: str = "english",
    platforms: Optional[list] = None,
) -> dict:
    if not platforms:
        platforms = ["instagram", "facebook", "twitter", "linkedin"]

    lang_instr = LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["english"])
    platform_styles = "\n".join([PLATFORM_CAPTION_STYLES[p] for p in platforms if p in PLATFORM_CAPTION_STYLES])

    system = f"You are a social media expert. {lang_instr} Respond with valid JSON only."
    prompt = f"""Generate social media captions and hashtags for this card:

Brand: {brand_name}
Title: {title}
Subtitle: {subtitle}
Content: {content}
Card Type: {template.replace('_', ' ').title()}

Platform caption styles:
{platform_styles}

Return ONLY this JSON:
{{
  "instagram": {{"caption": "...", "hashtags": ["tag1", "tag2", ...]}},
  "facebook": {{"caption": "...", "hashtags": ["tag1", "tag2"]}},
  "twitter": {{"caption": "...", "hashtags": ["tag1", "tag2"]}},
  "linkedin": {{"caption": "...", "hashtags": ["tag1", "tag2"]}},
  "whatsapp": {{"caption": "..."}}
}}

Include only the platforms requested: {platforms}
Hashtags without # prefix. 5-10 hashtags for Instagram, 2-3 for others."""

    try:
        raw = await _llm(prompt, system)
        data = _extract_json(raw)
        result = {}
        for p in platforms:
            if p in data:
                result[p] = data[p]
        result["provider"] = _active_provider()
        return result
    except Exception:
        fallback = {}
        tag_base = brand_name.lower().replace(" ", "") if brand_name else "brand"
        for p in platforms:
            fallback[p] = {
                "caption": f"{title}\n\n{subtitle}\n\n{content}".strip()[:250],
                "hashtags": [tag_base, "socialmedia", "branding", "marketing", "digital"],
            }
        fallback["provider"] = "fallback"
        return fallback


# ─── 4. IMAGE GENERATION ─────────────────────────────────────────────────────

IMAGE_GEN_PROVIDER = os.getenv("IMAGE_GEN_PROVIDER", "none")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")


async def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> Optional[bytes]:
    provider = IMAGE_GEN_PROVIDER.lower()

    if provider == "stability" and STABILITY_API_KEY:
        return await _stability_generate(prompt, width, height)
    elif provider == "replicate" and REPLICATE_API_TOKEN:
        return await _replicate_generate(prompt, width, height)
    return None


async def _stability_generate(prompt: str, width: int, height: int) -> Optional[bytes]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.stability.ai/v2beta/stable-image/generate/core",
            headers={
                "Authorization": f"Bearer {STABILITY_API_KEY}",
                "Accept": "image/*",
            },
            data={
                "prompt": prompt,
                "aspect_ratio": _aspect_ratio(width, height),
                "output_format": "png",
            },
            timeout=60,
        )
        if resp.status_code == 200:
            return resp.content
    return None


async def _replicate_generate(prompt: str, width: int, height: int) -> Optional[bytes]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions",
            headers={
                "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"input": {"prompt": prompt, "width": min(width, 1024), "height": min(height, 1024)}},
            timeout=10,
        )
        if resp.status_code != 201:
            return None
        prediction_url = resp.json().get("urls", {}).get("get")
        if not prediction_url:
            return None

        for _ in range(30):
            import asyncio
            await asyncio.sleep(2)
            poll = await client.get(prediction_url, headers={"Authorization": f"Bearer {REPLICATE_API_TOKEN}"})
            data = poll.json()
            if data.get("status") == "succeeded":
                output = data.get("output")
                if output:
                    img_url = output[0] if isinstance(output, list) else output
                    img_resp = await client.get(img_url, timeout=30)
                    return img_resp.content
            elif data.get("status") in ("failed", "canceled"):
                break
    return None


def _aspect_ratio(w: int, h: int) -> str:
    ratio = w / h
    if abs(ratio - 1) < 0.05:
        return "1:1"
    elif abs(ratio - 16/9) < 0.1:
        return "16:9"
    elif abs(ratio - 9/16) < 0.1:
        return "9:16"
    elif abs(ratio - 4/5) < 0.1:
        return "4:5"
    elif ratio > 1.5:
        return "16:9"
    else:
        return "1:1"


async def enhance_image_prompt(user_prompt: str, template: str, brand_name: str) -> str:
    system = "You are an AI image prompt engineer. Respond with only the enhanced prompt, no explanation."
    prompt = f"""Enhance this image generation prompt for a social media card background:

User prompt: {user_prompt}
Card type: {template.replace('_', ' ')}
Brand: {brand_name}

Create a detailed, vivid prompt (max 150 words) optimized for image generation.
Focus on: lighting, mood, composition, style. Make it suitable as a card background.
Do NOT include text or logos in the image description."""

    try:
        return await _llm(prompt, system)
    except Exception:
        return f"Professional {template.replace('_', ' ')} background, {user_prompt}, high quality, vibrant colors, suitable for social media"
