import os
import asyncio
from aiogram import Router, types, F, Bot
from bot.services.recognition_service import identify_music
from bot.services.downloader_service import search_youtube
from bot.handlers.downloader import media_cache
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(F.voice | F.audio)
async def handle_voice_recognition(message: types.Message, bot: Bot):
    status_msg = await message.reply("🔍 Musiqani eshityapman va aniqlashga harakat qilyapman...")
    
    # Create temp file path
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}.ogg" if message.voice else f"downloads/{file_id}_{message.audio.file_name}"
    
    try:
        await bot.download_file(file.file_path, file_path)
        
        # Identify music
        result = await identify_music(file_path)
        
        if result:
            title = result.get("title")
            artist = result.get("artist")
            
            await status_msg.edit_text(f"✅ Musiqa topildi!\n\n🎵 **{title}**\n👤 **{artist}**\n\nYouTube-dan yuklab olish variantlarini qidiryapman...")
            
            # Search on YouTube to get download buttons
            query = f"{artist} {title}"
            search_results = await search_youtube(query)
            
            if search_results:
                builder = InlineKeyboardBuilder()
                for i, res in enumerate(search_results[:5]):
                    callback_data = f"yt_{res['id']}_{message.message_id}"
                    builder.button(text=f"🎧 {res['title'][:30]}...", callback_data=callback_data)
                    # Store in cache for button handlers
                    media_cache[res['id']] = {
                        "title": res['title'],
                        "url": res['url'],
                        "orig_message_id": message.message_id
                    }
                
                builder.adjust(1)
                await message.reply(
                    f"👇 Ushbu qo'shiqni yuklab olishingiz mumkin:",
                    reply_markup=builder.as_markup()
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text(f"✅ Musiqa: **{title} - {artist}**\n\nAfsuski, YouTube'dan yuklab olish uchun variantlar topilmadi.")
        else:
            await status_msg.edit_text("❌ Afsuski, musiqani aniqlab bo'lmadi. Ovoz aniqroq chiqishiga yoki ko'proq (10-15 soniya) kuylashga harakat qiling.")
            
    except Exception as e:
        print(f"Voice recognition error: {e}", flush=True)
        await status_msg.edit_text("⚠️ Ovozli xabarni qayta ishlashda xatolik yuz berdi.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.message(F.content_type == types.ContentType.VOICE)
async def debug_voice(message: types.Message):
    print(f"Received voice: {message.voice.file_id}", flush=True)
