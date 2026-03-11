import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    from bot.main import run_bot, run_web
    import asyncio
    import threading
    
    # Run web server in a separate thread
    web_thread = threading.Thread(target=run_web, daemon=True)
    web_thread.start()
    
    # Run bot in the main loop
    asyncio.run(run_bot())
