from aiogram import Router, types, F
from bot.utils.link_parser import detect_platform
from bot.services.downloader_service import download_media
import os

router = Router()

@router.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    platform = detect_platform(url)
    
    if not platform:
        await message.reply("😔 Kechirasiz, bu havola qo'llab-quvvatlanmaydigan platformadan yoki noto'g'ri.")
        return
    
    status_msg = await message.answer(f"⏳ {platform.capitalize()} videosi tayyorlanmoqda...")
    
    file_path, title = await download_media(url, platform)
    
    if file_path and os.path.exists(file_path):
        await message.answer_video(
            video=types.FSInputFile(file_path),
            caption=f"✅ {title}\n\n@OmniSaveBot orqali yuklab olindi"
        )
        await status_msg.delete()
        os.remove(file_path)
    else:
        await status_msg.edit_text("❌ Xatolik yuz berdi. Videoni yuklab bo'lmadi.")
