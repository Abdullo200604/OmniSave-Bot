import os
import yt_dlp
from core.celery_app import celery_app

@celery_app.task(name="download_media_task")
def download_media_task(url, platform, chat_id):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'downloads/{chat_id}_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    if platform == 'tiktok':
        ydl_opts['extractor_args'] = {'tiktok': {'api_hostname': 'api16-normal'}}
        ydl_opts['http_headers'] = {'Referer': 'https://www.tiktok.com/'}
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            # In a real pro setup, we would send this file back via a bot instance or a webhook
            # For this MVP, we return the path and info
            return {
                "file_path": file_path,
                "title": info.get('title', 'video'),
                "chat_id": chat_id
            }
    except Exception as e:
        return {"error": str(e), "chat_id": chat_id}
