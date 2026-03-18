import aiohttp
import os
from bot import config

async def identify_music(audio_path: str):
    """
    Identifies music from an audio file using AudD API.
    Supports humming/singing.
    """
    if not config.AUDD_API_TOKEN:
        print("AudD API token not found.", flush=True)
        return None

    api_url = "https://api.audd.io/"
    
    # We use 'recognize' for normal recordings or humming. 
    # For better humming support, we can use the 'recognize' or 'recognizeWithOffset' if we want.
    # AudD automatically handles humming in recognize endpoint if it's clear.
    
    data = {
        'api_token': config.AUDD_API_TOKEN,
        'return': 'apple_music,spotify',
    }

    try:
        async with aiohttp.ClientSession() as session:
            with open(audio_path, 'rb') as f:
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
    
    return None
