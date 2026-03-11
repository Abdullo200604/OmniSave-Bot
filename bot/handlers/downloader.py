from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.downloader_service import extract_metadata, search_youtube
from bot.utils.link_parser import detect_platform
import os

router = Router()

# Simple in-memory cache for search results and media info
search_cache = {}
media_cache = {}

import re

@router.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    # Find all URLs in the message
    urls = re.findall(r'https?://\S+', message.text)
    
    if not urls:
        return

    for url in urls:
        platform = detect_platform(url)
        
        if not platform:
            await message.reply(
                f"😔 Kechirasiz, bu platforma hozircha qo'llab-quvvatlanmaydi: {url}\n\n"
                "📥 Men quyidagi platformalardan yuklay olaman:\n"
                "• YouTube, Instagram, TikTok, Facebook\n"
                "• Pinterest, Snapchat, Likee, VK, Threads"
            )
            continue

        status_msg = await message.answer(f"🔍 Havola tahlil qilinmoqda: {url}")
        
        metadata = await extract_metadata(url)
        if not metadata:
            await status_msg.edit_text(f"❌ Havoladan ma'lumot olib bo'lmadi: {url}\n\nHavola to'g'riligini tekshiring yoki keyinroq urinib ko'ring.")
            continue
        
        # Use normalized URL if returned
        final_url = metadata.get('url', url)
        chat_id = message.chat.id
        
        # Note: In multi-link scenario, media_cache might get overwritten 
        # but since we answer each one with buttons, we need a way to track which is which.
        # For now, let's keep it simple or use a better key.
        # Let's use a composite key for multi-link support or keep it as is if they answer one by one.
        media_cache[chat_id] = {"url": final_url, "metadata": metadata}
        
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
