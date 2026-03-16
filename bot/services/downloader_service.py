import yt_dlp
import asyncio
import os
import aiohttp
from bot import config

async def get_fastsaver_info(url: str):
    if not config.FASTSAVER_TOKEN:
        print("FastSaver token not found in config.", flush=True)
        return None
    api_url = "https://fastsaverapi.com/get-info"
    params = {"url": url, "token": config.FASTSAVER_TOKEN}
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            async with session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                print(f"FastSaver API response status: {resp.status}", flush=True)
                if resp.status == 200:
                    data = await resp.json()
                    if not data.get("error"):
                        return data
                    else:
                        print(f"FastSaver API returned error: {data.get('message')}", flush=True)
    except Exception as e:
        print(f"FastSaver API exception: {e}", flush=True)
    return None

async def get_rapidapi_info(url: str):
    if not config.RAPIDAPI_KEY or not config.RAPIDAPI_HOST:
        print("RapidAPI config missing.", flush=True)
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
                print(f"RapidAPI response status: {resp.status}", flush=True)
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"RapidAPI error response: {await resp.text()}", flush=True)
    except Exception as e:
        print(f"RapidAPI exception: {e}", flush=True)
    return None

async def resolve_redirect(url: str):
    try:
        async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
            async with session.head(url, allow_redirects=True, timeout=10) as resp:
                return str(resp.url)
    except:
        return url

async def extract_metadata(url: str):
    print(f"Extracting metadata for: {url}", flush=True)
    original_url = url

    # Normalize Threads.com to Threads.net
    if "threads.com" in url:
        url = url.replace("threads.com", "threads.net")
    
    # helper for yt-dlp attempt
    async def try_ytdlp(target_url):
        print("Trying yt-dlp...", flush=True)
        if "facebook.com/share" in target_url:
            print("Resolving Facebook share redirect for yt-dlp...", flush=True)
            target_url = await resolve_redirect(target_url)
            print(f"Resolved URL for yt-dlp: {target_url}", flush=True)

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        cookie_opts = get_cookie_opts()
        for ua in user_agents:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'user_agent': ua,
                'referer': 'https://www.google.com/',
                'nocheckcertificate': True,
                'geo_bypass': True,
                **cookie_opts
            }
            loop = asyncio.get_event_loop()
            try:
                info = await loop.run_in_executor(None, lambda: extract_info(target_url, ydl_opts, download=False))
                if info:
                    print(f"yt-dlp success: {info.get('title')}", flush=True)
                    return {
                        "title": info.get('title'),
                        "artist": info.get('artist') or info.get('uploader'),
                        "track": info.get('track'),
                        "duration": info.get('duration'),
                        "url": target_url
                    }
            except Exception as e:
                print(f"yt-dlp attempt failure with UA {ua}: {e}", flush=True)
        return None

    is_fb_insta = "facebook.com" in url or "instagram.com" in url
    has_cookies = os.path.exists("cookies.txt")
    
    # If FB/Insta and NO cookies, APIs are mandatory
    if is_fb_insta and not has_cookies:
        print("FB/Insta and no cookies.txt detecting. Using APIs as primary.", flush=True)
        fs_data = await get_fastsaver_info(original_url)
        if fs_data:
            return {
                "title": fs_data.get('caption') or "Video",
                "artist": fs_data.get('hosting') or "FastSaver",
                "track": fs_data.get('shortcode'),
                "url": original_url,
                "download_url": fs_data.get('download_url'),
                "thumb": fs_data.get('thumb')
            }
        # fallback to RapidAPI
        ra_data = await get_rapidapi_info(original_url)
        if ra_data and ra_data.get("url"):
            return {
                "title": ra_data.get('title') or "Video",
                "artist": "RapidAPI",
                "url": original_url,
                "download_url": ra_data.get("url"),
                "thumb": ra_data.get('thumbnail')
            }

    # Otherwise (or if APIs failed), try yt-dlp
    res = await try_ytdlp(url)
    if res: return res

    # If yt-dlp failed and we haven't tried APIs yet (non FB/Insta case)
    if not (is_fb_insta and not has_cookies):
        fs_data = await get_fastsaver_info(original_url)
        if fs_data:
            return {
                "title": fs_data.get('caption') or "Video",
                "artist": fs_data.get('hosting') or "FastSaver",
                "track": fs_data.get('shortcode'),
                "url": original_url,
                "download_url": fs_data.get('download_url'),
                "thumb": fs_data.get('thumb')
            }
        ra_data = await get_rapidapi_info(original_url)
        if ra_data and ra_data.get("url"):
            return {
                "title": ra_data.get('title') or "Video",
                "artist": "RapidAPI",
                "url": original_url,
                "download_url": ra_data.get("url"),
                "thumb": ra_data.get('thumbnail')
            }

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
                        return output_path
        except Exception as e:
            print(f"Direct audio download error: {e}")

    # Fallback/Default yt-dlp download
    cookie_opts = get_cookie_opts()
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
        **cookie_opts,
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

    cookie_opts = get_cookie_opts()
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
        **cookie_opts
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
