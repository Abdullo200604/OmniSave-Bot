from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.downloader_service import download_audio
from bot.services.audio_processor import apply_slowed, apply_8d, apply_bass_boost
from bot.handlers.downloader import search_cache
import os
import uuid

router = Router()

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
