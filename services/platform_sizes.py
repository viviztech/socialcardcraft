PLATFORM_SIZES = {
    # Instagram
    "instagram_square": {
        "label": "Instagram Post (Square)",
        "platform": "Instagram",
        "width": 1080,
        "height": 1080,
        "aspect": "1:1",
        "icon": "instagram",
    },
    "instagram_portrait": {
        "label": "Instagram Post (Portrait)",
        "platform": "Instagram",
        "width": 1080,
        "height": 1350,
        "aspect": "4:5",
        "icon": "instagram",
    },
    "instagram_story": {
        "label": "Instagram Story / Reel Cover",
        "platform": "Instagram",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "icon": "instagram",
    },
    # Facebook
    "facebook_post": {
        "label": "Facebook Post",
        "platform": "Facebook",
        "width": 1200,
        "height": 630,
        "aspect": "1.91:1",
        "icon": "facebook",
    },
    "facebook_story": {
        "label": "Facebook Story",
        "platform": "Facebook",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "icon": "facebook",
    },
    "facebook_cover": {
        "label": "Facebook Cover Photo",
        "platform": "Facebook",
        "width": 820,
        "height": 312,
        "aspect": "2.63:1",
        "icon": "facebook",
    },
    # X / Twitter
    "twitter_post": {
        "label": "X / Twitter Post",
        "platform": "X (Twitter)",
        "width": 1200,
        "height": 675,
        "aspect": "16:9",
        "icon": "twitter",
    },
    "twitter_header": {
        "label": "X / Twitter Header",
        "platform": "X (Twitter)",
        "width": 1500,
        "height": 500,
        "aspect": "3:1",
        "icon": "twitter",
    },
    # LinkedIn
    "linkedin_post": {
        "label": "LinkedIn Post",
        "platform": "LinkedIn",
        "width": 1200,
        "height": 627,
        "aspect": "1.91:1",
        "icon": "linkedin",
    },
    "linkedin_banner": {
        "label": "LinkedIn Banner",
        "platform": "LinkedIn",
        "width": 1584,
        "height": 396,
        "aspect": "4:1",
        "icon": "linkedin",
    },
    # YouTube
    "youtube_thumbnail": {
        "label": "YouTube Thumbnail",
        "platform": "YouTube",
        "width": 1280,
        "height": 720,
        "aspect": "16:9",
        "icon": "youtube",
    },
    "youtube_channel_art": {
        "label": "YouTube Channel Art",
        "platform": "YouTube",
        "width": 2560,
        "height": 1440,
        "aspect": "16:9",
        "icon": "youtube",
    },
    # Pinterest
    "pinterest_pin": {
        "label": "Pinterest Pin",
        "platform": "Pinterest",
        "width": 1000,
        "height": 1500,
        "aspect": "2:3",
        "icon": "pinterest",
    },
    # WhatsApp
    "whatsapp_status": {
        "label": "WhatsApp Status",
        "platform": "WhatsApp",
        "width": 1080,
        "height": 1920,
        "aspect": "9:16",
        "icon": "whatsapp",
    },
    # Google Business
    "google_business": {
        "label": "Google Business Post",
        "platform": "Google",
        "width": 1200,
        "height": 1200,
        "aspect": "1:1",
        "icon": "google",
    },
}


def get_sizes_by_platform():
    platforms = {}
    for key, val in PLATFORM_SIZES.items():
        p = val["platform"]
        if p not in platforms:
            platforms[p] = []
        platforms[p].append({"key": key, **val})
    return platforms


def get_size(key: str) -> dict:
    return PLATFORM_SIZES.get(key)
