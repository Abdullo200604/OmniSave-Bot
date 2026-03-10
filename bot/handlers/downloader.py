from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.downloader_service import extract_metadata, search_youtube
import os

router = Router()

# Simple in-memory cache for search results (in production use Redis)
search_cache = {}

@router.message(F.text.contains("http"))
async def handle_link(message: types.Message):
    url = message.text
    status_msg = await message.answer("🔍 Havola tahlil qilinmoqda...")
    
    metadata = await extract_metadata(url)
    if not metadata:
        await status_msg.edit_text("❌ Havoladan ma'lumot olib bo'lmadi.")
        return
    
    query = metadata.get('title') or metadata.get('track') or "music"
    artist = metadata.get('artist') or ""
    
    await status_msg.edit_text(f"🎵 Topilgan: **{query}** {artist}\n🔎 YouTube-dan qidirilmoqda...")
    
    results = await search_youtube(f"{query} {artist}", limit=10)
    if not results:
        await status_msg.edit_text("❌ Hech qanday natija topilmadi.")
        return
    
    chat_id = message.chat.id
    search_cache[chat_id] = results
    
    text = f"🎵 **Musiqa:** {query}\n👤 **Artis:** {artist}\n\n**Mavjud versiyalar:**\n\n"
    builder = InlineKeyboardBuilder()
    
    for i, res in enumerate(results, 1):
        text += f"{i}. {res['title']}\n"
        builder.button(text=f"[{i}]", callback_data=f"select_{i-1}")
    
    builder.adjust(5) # 5 buttons per row
    
    await status_msg.delete()
    await message.answer(text, reply_markup=builder.as_markup())
