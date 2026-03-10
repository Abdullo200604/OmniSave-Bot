# OmniSave Bot 🚀

OmniSave is a professional Telegram bot built with Python and Aiogram 3.x that allows users to download videos and images from various social media platforms using `yt-dlp`.

## Features 🌟
- **Multi-platform support**: YouTube, Instagram, TikTok, Pinterest, Snapchat, Likee, VK, Facebook, Threads, and Music platforms.
- **Auto-detection**: Automatically detects the platform from the link.
- **Fast & Async**: Built with an asynchronous architecture for high performance.
- **Background Processing**: Uses Celery and Redis for efficient task handling.
- **Easy Deployment**: Ready to be deployed on Railway.com or via Docker.
- **Health Check**: Integrated FastAPI server for monitoring.

## Supported Platforms 🌐
- YouTube  
- Instagram  
- TikTok  
- Pinterest  
- Snapchat  
- Likee  
- VK  
- Facebook  
- Threads  
- Music  

## Tech Stack 🛠️
- **Language**: Python 3.10+
- **Framework**: [Aiogram 3.x](https://github.com/aiogram/aiogram)
- **Downloader**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Task Queue**: Celery + Redis
- **Web Server**: FastAPI
- **Containerization**: Docker & Docker Compose

## Quick Start 🚀

### 1. Prerequisites
- Python 3.10 or higher
- Docker (optional, but recommended)
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### 2. Manual Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd OmniSave
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your token:
   ```env
   BOT_TOKEN=your_token_here
   REDIS_URL=redis://localhost:6379/0
   ```
4. Run the bot:
   ```bash
   python bot/main.py
   ```

### 3. Docker Setup
```bash
docker-compose up --build
```

## Deployment ☁️
This bot is pre-configured for **Railway.com**. Simply connect your GitHub repository to Railway, and it will automatically detect the `Dockerfile` and deploy the bot.

## License 📄
This project is licensed under the MIT License.
