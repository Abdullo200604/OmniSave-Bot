import aiohttp
import os
import asyncio
from bot import config

async def convert_to_mp3(input_path: str) -> str:
    """Converts audio file to MP3 using FFmpeg."""
    output_path = input_path.rsplit('.', 1)[0] + ".mp3"
    try:
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-y', '-i', input_path, '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if os.path.exists(output_path):
            return output_path
    except Exception as e:
        print(f"FFmpeg conversion error: {e}")
    return input_path

async def identify_music(audio_path: str):
    """
    Identifies music from an audio file using AudD API.
    Supports humming/singing.
    """
    if not config.AUDD_API_TOKEN:
        print("AudD API token not found.", flush=True)
        return None

    # Convert to standard MP3 to ensure compatibility with AudD
    mp3_path = await convert_to_mp3(audio_path)

    api_url = "https://api.audd.io/"
    
    data = {
        'api_token': config.AUDD_API_TOKEN,
        'return': 'apple_music,spotify',
    }

    try:
        async with aiohttp.ClientSession() as session:
            with open(mp3_path, 'rb') as f:
                form = aiohttp.FormData()
                form.add_field('file', f)
                for key, value in data.items():
                    form.add_field(key, value)
                
                async with session.post(api_url, data=form) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        if result.get("status") == "success" and result.get("result"):
                            return result["result"]
                        else:
                            print(f"AudD returned no match or error: {result.get('error')}", flush=True)
                    else:
                        print(f"AudD API request failed with status {resp.status}", flush=True)
    except Exception as e:
        print(f"AudD service exception: {e}", flush=True)
    finally:
        # Clean up the converted MP3 if it was created
        if mp3_path != audio_path and os.path.exists(mp3_path):
            os.remove(mp3_path)
    
    return None
