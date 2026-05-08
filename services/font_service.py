LANGUAGE_FONTS = {
    "english": {
        "label": "English",
        "script": "Latin",
        "google_font": "Poppins",
        "weights": "300;400;600;700",
        "css_family": "'Poppins', sans-serif",
        "direction": "ltr",
        "body_font": "Inter",
        "body_weights": "400;500",
        "body_family": "'Inter', sans-serif",
    },
    "hindi": {
        "label": "हिंदी (Hindi)",
        "script": "Devanagari",
        "google_font": "Noto+Sans+Devanagari",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Devanagari', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Devanagari",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Devanagari', sans-serif",
    },
    "tamil": {
        "label": "தமிழ் (Tamil)",
        "script": "Tamil",
        "google_font": "Noto+Sans+Tamil",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Tamil', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Tamil",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Tamil', sans-serif",
    },
    "telugu": {
        "label": "తెలుగు (Telugu)",
        "script": "Telugu",
        "google_font": "Noto+Sans+Telugu",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Telugu', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Telugu",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Telugu', sans-serif",
    },
    "kannada": {
        "label": "ಕನ್ನಡ (Kannada)",
        "script": "Kannada",
        "google_font": "Noto+Sans+Kannada",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Kannada', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Kannada",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Kannada', sans-serif",
    },
    "malayalam": {
        "label": "മലയാളം (Malayalam)",
        "script": "Malayalam",
        "google_font": "Noto+Sans+Malayalam",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Malayalam', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Malayalam",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Malayalam', sans-serif",
    },
    "bengali": {
        "label": "বাংলা (Bengali)",
        "script": "Bengali",
        "google_font": "Noto+Sans+Bengali",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Bengali', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Bengali",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Bengali', sans-serif",
    },
    "marathi": {
        "label": "मराठी (Marathi)",
        "script": "Devanagari",
        "google_font": "Noto+Sans+Devanagari",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Devanagari', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Devanagari",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Devanagari', sans-serif",
    },
    "gujarati": {
        "label": "ગુજરાતી (Gujarati)",
        "script": "Gujarati",
        "google_font": "Noto+Sans+Gujarati",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Gujarati', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Gujarati",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Gujarati', sans-serif",
    },
    "punjabi": {
        "label": "ਪੰਜਾਬੀ (Punjabi)",
        "script": "Gurmukhi",
        "google_font": "Noto+Sans+Gurmukhi",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Gurmukhi', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Gurmukhi",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Gurmukhi', sans-serif",
    },
    "odia": {
        "label": "ଓଡ଼ିଆ (Odia)",
        "script": "Odia",
        "google_font": "Noto+Sans+Oriya",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Oriya', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Oriya",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Oriya', sans-serif",
    },
    "urdu": {
        "label": "اردو (Urdu)",
        "script": "Arabic",
        "google_font": "Noto+Nastaliq+Urdu",
        "weights": "400;600;700",
        "css_family": "'Noto Nastaliq Urdu', serif",
        "direction": "rtl",
        "body_font": "Noto+Nastaliq+Urdu",
        "body_weights": "400;500",
        "body_family": "'Noto Nastaliq Urdu', serif",
    },
    "assamese": {
        "label": "অসমীয়া (Assamese)",
        "script": "Bengali",
        "google_font": "Noto+Sans+Bengali",
        "weights": "400;600;700",
        "css_family": "'Noto Sans Bengali', sans-serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Bengali",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Bengali', sans-serif",
    },
    "sanskrit": {
        "label": "संस्कृत (Sanskrit)",
        "script": "Devanagari",
        "google_font": "Tiro+Devanagari+Sanskrit",
        "weights": "400",
        "css_family": "'Tiro Devanagari Sanskrit', serif",
        "direction": "ltr",
        "body_font": "Noto+Sans+Devanagari",
        "body_weights": "400;500",
        "body_family": "'Noto Sans Devanagari', sans-serif",
    },
}


def get_font_config(language: str) -> dict:
    return LANGUAGE_FONTS.get(language, LANGUAGE_FONTS["english"])


def get_google_fonts_url(language: str) -> str:
    config = get_font_config(language)
    fonts = []
    head_font = f"family={config['google_font']}:wght@{config['weights']}"
    fonts.append(head_font)
    if config["body_font"] != config["google_font"]:
        body_font = f"family={config['body_font']}:wght@{config['body_weights']}"
        fonts.append(body_font)
    if language != "english":
        fonts.append("family=Poppins:wght@400;600;700")
    query = "&".join(fonts)
    return f"https://fonts.googleapis.com/css2?{query}&display=swap"


def get_all_languages():
    return {k: v["label"] for k, v in LANGUAGE_FONTS.items()}
