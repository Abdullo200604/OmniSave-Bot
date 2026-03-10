from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    start_text = (
        "📥 Men sizga quyidagi platformalardan video va rasmlarni yuklashda yordam beraman:\n\n"
        "🌐 YouTube\n"
        "🌐 Instagram\n"
        "🌐 TikTok\n"
        "🌐 Pinterest\n"
        "🌐 Snapchat\n"
        "🌐 Likee\n"
        "🌍 VK\n"
        "🌐 Facebook\n"
        "🌐 Threads\n"
        "🎵 Music\n\n"
        "• Videoni yuklash uchun video yoki rasm havolasini menga jo’nating.\n\n"
        "(Bot guruhlarda ham ishlaydi)"
    )
    await message.answer(start_text)
