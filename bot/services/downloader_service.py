import yt_dlp
import asyncio
import os

async def extract_metadata(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=False))
        return {
            "title": info.get('title'),
            "artist": info.get('artist') or info.get('uploader'),
            "track": info.get('track'),
            "duration": info.get('duration'),
        }
    except Exception as e:
        print(f"Metadata extraction error: {e}")
        return None

async def search_youtube(query: str, limit: int = 10):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
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
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=True))
        # yt-dlp might add .mp3 extension
        if not output_path.endswith('.mp3'):
            actual_path = output_path + '.mp3'
        else:
            actual_path = output_path
        return actual_path
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def download_video(url: str, output_path: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
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
