import yt_dlp
import asyncio
import os

async def download_media(url: str, platform: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    # Platform-specific tweaks
    if platform == 'tiktok':
        ydl_opts['extractor_args'] = {'tiktok': {'api_hostname': 'api16-normal'}}
        ydl_opts['http_headers'] = {'Referer': 'https://www.tiktok.com/'}
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts))
        return info['requested_downloads'][0]['filepath'], info.get('title', 'video')
    except Exception as e:
        print(f"Download error: {e}")
        return None, None

def extract_info(url, opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=True)
