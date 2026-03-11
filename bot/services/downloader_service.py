import yt_dlp
import asyncio
import os
import aiohttp
from bot import config

async def get_fastsaver_info(url: str):
    if not config.FASTSAVER_TOKEN:
        print("FastSaver token not found in config.")
        return None
    api_url = "https://fastsaverapi.com/get-info"
    params = {"url": url, "token": config.FASTSAVER_TOKEN}
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                print(f"FastSaver API response status: {resp.status}")
                if resp.status == 200:
                    data = await resp.json()
                    if not data.get("error"):
                        return data
                    else:
                        print(f"FastSaver API returned error: {data.get('message')}")
    except Exception as e:
        print(f"FastSaver API exception: {e}")
    return None

async def get_rapidapi_info(url: str):
    if not config.RAPIDAPI_KEY or not config.RAPIDAPI_HOST:
        print("RapidAPI config missing.")
        return None
    api_url = f"https://{config.RAPIDAPI_HOST}/"
    headers = {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": config.RAPIDAPI_HOST,
        "User-Agent": "Mozilla/5.0"
    }
    params = {"url": url}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                print(f"RapidAPI response status: {resp.status}")
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"RapidAPI error response: {await resp.text()}")
    except Exception as e:
        print(f"RapidAPI exception: {e}")
    return None

async def resolve_redirect(url: str):
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            async with session.head(url, allow_redirects=True, timeout=10) as resp:
                return str(resp.url)
    except:
        return url

async def extract_metadata(url: str):
    print(f"Extracting metadata for: {url}")
    
    # Try to resolve redirects for Facebook share links
    if "facebook.com/share" in url:
        print("Resolving Facebook share redirect...")
        url = await resolve_redirect(url)
        print(f"Resolved URL: {url}")

    # Normalize Threads.com to Threads.net
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
    
    # 1. Try FastSaver first
    print("Trying FastSaver API...")
    fs_data = await get_fastsaver_info(url)
    if fs_data:
        print(f"FastSaver success: {fs_data.get('hosting')}")
        return {
            "title": fs_data.get('caption') or "Video",
            "artist": fs_data.get('hosting') or "FastSaver",
            "track": fs_data.get('shortcode'),
            "duration": None,
            "url": url,
            "download_url": fs_data.get('download_url'),
            "thumb": fs_data.get('thumb')
        }
        
    # 2. Try RapidAPI fallback
    print("Trying RapidAPI...")
    ra_data = await get_rapidapi_info(url)
    if ra_data and ra_data.get("url"):
        print("RapidAPI success")
        return {
            "title": ra_data.get('title') or "Video",
            "artist": "RapidAPI",
            "track": None,
            "duration": None,
            "url": url,
            "download_url": ra_data.get('url'),
            "thumb": ra_data.get('thumbnail')
        }
        
    # 3. Fallback to yt-dlp
    print("Trying yt-dlp fallback...")
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
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
            # 'impersonate': 'chrome', # Disabling for now due to dependency issues
        }
        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=False))
            if info:
                print(f"yt-dlp success: {info.get('title')}")
                return {
                    "title": info.get('title'),
                    "artist": info.get('artist') or info.get('uploader'),
                    "track": info.get('track'),
                    "duration": info.get('duration'),
                    "url": url
                }
        except Exception as e:
            print(f"yt-dlp attempt failure with UA {ua}: {e}")
            
    print("All metadata extraction methods failed.")
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

async def download_audio(url: str, output_path: str, direct_url: str = None):
    # If we have a direct download URL from API, use aiohttp to download it
    if direct_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(direct_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        # We might need to convert it to mp3 if it's not already
                        # But for now let's assume direct_url is usable or handled by handler
                        return output_path
        except Exception as e:
            print(f"Direct audio download error: {e}")

    # Fallback/Default yt-dlp download
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'impersonate': 'chrome',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: extract_info(url, ydl_opts, download=True))
        actual_path = output_path if output_path.endswith('.mp3') else output_path + '.mp3'
        return actual_path
    except Exception as e:
        print(f"Download error: {e}")
        return None

async def download_video(url: str, output_path: str, direct_url: str = None):
    if direct_url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(direct_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_path, 'wb') as f:
                            f.write(content)
                        return output_path
        except Exception as e:
            print(f"Direct video download error: {e}")

    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'nocheckcertificate': True,
        'geo_bypass': True,
        'impersonate': 'chrome',
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
