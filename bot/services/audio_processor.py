import subprocess
import os

async def apply_slowed(input_path: str, output_path: str):
    # Slowed: lower speed and pitch (0.8x)
    # FFmpeg filter: atempo=0.8,asetrate=44100*0.8,aresample=44100
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter_complex", "asetrate=44100*0.8,aresample=44100,atempo=1.0", 
        output_path
    ]
    # Note: asetrate changes BOTH pitch and speed. atempo=1.0 keeps it at the speed set by asetrate.
    # Actually slowed usually means lower pitch AND speed.
    # Pure slowed: asetrate=44100*0.8,aresample=44100
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", "asetrate=44100*0.8,aresample=44100",
        output_path
    ]
    return await run_ffmpeg(cmd)

async def apply_8d(input_path: str, output_path: str):
    # 8D Audio: spatial rotate (apulsator filter)
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", "apulsator=hz=0.1",
        output_path
    ]
    return await run_ffmpeg(cmd)

async def apply_bass_boost(input_path: str, output_path: str):
    # Bass Boost: increase low frequencies (equalizer)
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", "equalizer=f=60:width_type=h:w=50:g=10",
        output_path
    ]
    return await run_ffmpeg(cmd)

async def run_ffmpeg(cmd):
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process.communicate()
        return process.returncode == 0
    except Exception as e:
        print(f"FFmpeg error: {e}")
        return False

import asyncio
