from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.downloader_service import extract_metadata, search_youtube
from bot.utils.link_parser import detect_platform
import os

router = Router()

# Simple in-memory cache for search results and media info
search_cache = {}
media_cache = {}

@router.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    platform = detect_platform(url)
    
    if not platform:
        await message.reply(
            "😔 Kechirasiz, bu platforma hozircha qo'llab-quvvatlanmaydi.\n\n"
            "📥 Men quyidagi platformalardan yuklay olaman:\n"
            "• YouTube, Instagram, TikTok, Facebook\n"
            "• Pinterest, Snapchat, Likee, VK, Threads"
        )
        return

    status_msg = await message.answer("🔍 Havola tahlil qilinmoqda...")
    
    metadata = await extract_metadata(url)
    if not metadata:
        await status_msg.edit_text("❌ Havoladan ma'lumot olib bo'lmadi. Havola to'g'riligini tekshiring.")
        return
    
    chat_id = message.chat.id
    media_cache[chat_id] = {"url": url, "metadata": metadata}
    
    title = metadata.get('title') or "Video"
    artist = metadata.get('artist') or ""
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📹 Videoni yuklash", callback_data="media_download_video")
    builder.button(text="🎵 Musiqani aniqlash", callback_data="media_search_music")
    builder.adjust(1)
    
    await status_msg.delete()
    await message.answer(
        f"✅ Ma'lumot topildi:\n\n"
        f"📝 **Nomi:** {title}\n"
        f"👤 **Muallif:** {artist}\n\n"
        f"Nima qilmoqchisiz?",
        reply_markup=builder.as_markup()
    )
