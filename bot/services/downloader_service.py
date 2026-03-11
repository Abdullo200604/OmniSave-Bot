import yt_dlp
import asyncio
import os

async def extract_metadata(url: str):
    # Normalize Threads.com to Threads.net
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
        
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
    ]
    
    for ua in user_agents:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'user_agent': ua,
            'referer': 'https://www.google.com/',
            'nocheckcertificate': True,
            'geo_bypass': True,
            'ignoreerrors': False,
            'no_color': True,
        }
        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=False))
            if info:
                return {
                    "title": info.get('title'),
                    "artist": info.get('artist') or info.get('uploader'),
                    "track": info.get('track'),
                    "duration": info.get('duration'),
                    "url": url # Return normalized url
                }
        except Exception as e:
            print(f"Metadata extraction attempt failure with UA {ua}: {e}")
            continue # Try next UA
            
    return None

async def search_youtube(query: str, limit: int = 10):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    loop = asyncio.get_event_loop()
    try:
        search_url = f"ytsearch{limit}:{query}"
        info = await loop.run_in_executor(None, lambda: extract_info(search_url, ydl_opts, download=False))
        entries = info.get('entries', [])
        results = []
        for entry in entries:
            results.append({
                "id": entry.get('id'),
                "title": entry.get('title'),
                "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                "duration": entry.get('duration'),
            })
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

async def download_audio(url: str, output_path: str):
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=True))
        if not output_path.endswith('.mp3'):
            actual_path = output_path + '.mp3'
        else:
            actual_path = output_path
        return actual_path
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def download_video(url: str, output_path: str):
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
        
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'geo_bypass': True,
    }
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=True))
        return output_path
    except Exception as e:
        print(f"Video download error: {e}")
        return None

def extract_info(url, opts, download=True):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=download)
