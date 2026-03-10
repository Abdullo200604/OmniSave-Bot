import re

PLATFORMS = {
    "youtube": [r"youtube\.com", r"youtu\.be"],
    "instagram": [r"instagram\.com"],
    "tiktok": [r"tiktok\.com"],
    "pinterest": [r"pinterest\.com", r"pin\.it"],
    "snapchat": [r"snapchat\.com"],
    "likee": [r"likee\.video"],
    "vk": [r"vk\.com"],
    "facebook": [r"facebook\.com", r"fb\.watch"],
    "threads": [r"threads\.net"],
}

def detect_platform(url: str) -> str:
    for platform, patterns in PLATFORMS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return None
