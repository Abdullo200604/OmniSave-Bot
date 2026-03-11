from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.downloader_service import download_audio, download_video, search_youtube
from bot.services.audio_processor import apply_slowed, apply_8d, apply_bass_boost
from bot.handlers.downloader import search_cache, media_cache
import os
import uuid

router = Router()

@router.callback_query(F.data == "media_download_video")
async def handle_video_download(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id not in media_cache:
        await callback.answer("❌ Ma'lumot eskirgan.")
        return
    
    data = media_cache[chat_id]
    direct_url = data['metadata'].get("download_url")
    await callback.message.edit_text("⏳ Video yuklanmoqda...")
    
    file_id = str(uuid.uuid4())
    temp_path = f"downloads/{file_id}.mp4"
    
    path = await download_video(data['url'], temp_path, direct_url=direct_url)
    if path and os.path.exists(path):
        await callback.message.delete()
        await callback.message.answer_video(
            video=types.FSInputFile(path),
            caption=f"✅ {data['metadata'].get('title', 'Video')}"
        )
        os.remove(path)
    else:
        await callback.message.edit_text("❌ Videoni yuklashda xatolik yuz berdi.")

@router.callback_query(F.data == "media_search_music")
async def handle_music_search(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id not in media_cache:
        await callback.answer("❌ Ma'lumot eskirgan.")
        return
    
    data = media_cache[chat_id]
    metadata = data['metadata']
    
    query = metadata.get('title') or metadata.get('track') or "music"
    artist = metadata.get('artist') or ""
    
    await callback.message.edit_text("🔎 YouTube-dan qidirilmoqda...")
    
    results = await search_youtube(f"{query} {artist}", limit=10)
    if not results:
        await callback.message.edit_text("❌ Hech qanday musiqa topilmadi.")
        return
    
    search_cache[chat_id] = results
    
    text = f"🎵 **Musiqa:** {query}\n👤 **Artis:** {artist}\n\n**Mavjud versiyalar:**\n\n"
    builder = InlineKeyboardBuilder()
    
    for i, res in enumerate(results, 1):
        text += f"{i}. {res['title']}\n"
        builder.button(text=f"[{i}]", callback_data=f"select_{i-1}")
    
    builder.adjust(5)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("select_"))
async def handle_selection(callback: types.CallbackQuery):
    idx = int(callback.data.split("_")[1])
    chat_id = callback.message.chat.id
    
    if chat_id not in search_cache:
        await callback.answer("❌ Qidiruv natijalari eskirgan.")
        return
    
    selection = search_cache[chat_id][idx]
    await callback.message.edit_text(f"⏳ **{selection['title']}** yuklanmoqda...")
    
    file_id = str(uuid.uuid4())
    temp_path = f"downloads/{file_id}"
    
    actual_path = await download_audio(selection['url'], temp_path)
    
    if actual_path and os.path.exists(actual_path):
        builder = InlineKeyboardBuilder()
        builder.button(text="🐌 Slowed", callback_data=f"effect_slowed_{file_id}")
        builder.button(text="🎧 8D Audio", callback_data=f"effect_8d_{file_id}")
        builder.button(text="🔊 Bass Boost", callback_data=f"effect_bass_{file_id}")
        builder.adjust(1)
        
        await callback.message.delete()
        await callback.message.answer_audio(
            audio=types.FSInputFile(actual_path),
            caption=f"✅ {selection['title']}\n\nEffektini tanlang:",
            reply_markup=builder.as_markup()
        )
        # Note: We keep the original file for processing
    else:
        await callback.message.edit_text("❌ Yuklashda xatolik yuz berdi.")

@router.callback_query(F.data.startswith("effect_"))
async def handle_effect(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    effect = parts[1]
    file_id = parts[2]
    
    input_path = f"downloads/{file_id}.mp3"
    output_path = f"downloads/{file_id}_{effect}.mp3"
    
    if not os.path.exists(input_path):
        await callback.answer("❌ Asl fayl topilmadi.")
        return
    
    await callback.answer(f"⏳ {effect.capitalize()} effekt berilmoqda...")
    
    success = False
    if effect == "slowed":
        success = await apply_slowed(input_path, output_path)
    elif effect == "8d":
        success = await apply_8d(input_path, output_path)
    elif effect == "bass":
        success = await apply_bass_boost(input_path, output_path)
    
    if success and os.path.exists(output_path):
        await callback.message.answer_audio(
            audio=types.FSInputFile(output_path),
            caption=f"✨ {effect.capitalize()} versiyasi tayyor!"
        )
        os.remove(output_path)
    else:
        await callback.answer("❌ Effekt berishda xatolik.")
