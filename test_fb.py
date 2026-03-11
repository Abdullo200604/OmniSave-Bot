import asyncio
import os
from bot.services.downloader_service import extract_metadata, download_video
from dotenv import load_dotenv

async def test_facebook():
    # Lokal testda Edge brauzer cookie-laridan foydalanish uchun:
    os.environ["USE_BROWSER_COOKIES"] = "True"
    load_dotenv()
    url = "https://www.facebook.com/share/p/18NSZNu88X/"
    print(f"--- Lokal Test Boshlandi ---")
    print(f"Havola: {url}\n")
    
    # 1. Metadata extraction testi
    print("1. Metadata olishga urinish...")
    metadata = await extract_metadata(url)
    
    if metadata:
        print(f"✅ Metadata topildi!")
        print(f"Sarlavha: {metadata.get('title')}")
        print(f"Manba: {metadata.get('artist')}")
        
        if metadata.get('download_url'):
            print(f"🔗 To'g'ridan-to'g'ri yuklash havolasi: {metadata['download_url'][:50]}...")
            
            # 2. Yuklab olish testi
            print("\n2. Videoni yuklab olishga urinish...")
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
                
            output_path = "downloads/test_fb.mp4"
            result_path = await download_video(url, output_path, direct_url=metadata.get('download_url'))
            
            if result_path and os.path.exists(result_path):
                print(f"✅ Video muvaffaqiyatli yuklandi: {result_path}")
                print(f"Fayl hajmi: {os.path.getsize(result_path)} bytes")
            else:
                print("❌ Videoni yuklab bo'lmadi.")
        else:
            print("⚠️ Metadata bor, lekin to'g'ridan-to'g'ri yuklash havolasi yo'q (yt-dlp fallback bo'lgan bo'lishi mumkin).")
    else:
        print("❌ Hech qanday metadata olib bo'lmadi.")

if __name__ == "__main__":
    asyncio.run(test_facebook())
