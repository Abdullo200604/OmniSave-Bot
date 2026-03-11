import re

PLATFORMS = {
    "youtube": [r"youtube\.com", r"youtu\.be", r"music\.youtube\.com"],
    "instagram": [r"instagram\.com", r"instagr\.am", r"ig\.me"],
    "tiktok": [r"tiktok\.com", r"vm\.tiktok\.com", r"vt\.tiktok\.com"],
    "pinterest": [r"pinterest\.com", r"pin\.it", r"pinterest\.it"],
    "snapchat": [r"snapchat\.com", r"story\.snapchat\.com"],
    "likee": [r"likee\.video", r"likee\.com"],
    "vk": [r"vk\.com", r"vkontakte\.ru"],
    "facebook": [r"facebook\.com", r"fb\.watch", r"fb\.com", r"m\.facebook\.com"],
    "threads": [r"threads\.net", r"threads\.com"],
}

def detect_platform(url: str) -> str:
    for platform, patterns in PLATFORMS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return None
