import asyncio
import uvicorn
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN, PORT
from bot.handlers import start, downloader, audio_handler
from web.server import app as web_app
import threading

async def run_bot():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(start.router)
    dp.include_router(downloader.router)
    dp.include_router(audio_handler.router)
    
    print("Bot is starting...")
    import os
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    await dp.start_polling(bot)

def run_web():
    uvicorn.run(web_app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    asyncio.run(run_bot())
