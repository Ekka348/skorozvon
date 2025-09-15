import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Skorozvon API Configuration
    SKOROZVON_API_URL = "https://api.skorozvon.ru"
    SKOROZVON_USERNAME = os.getenv("SKOROZVON_USERNAME")
    SKOROZVON_API_KEY = os.getenv("SKOROZVON_API_KEY")
    SKOROZVON_CLIENT_ID = os.getenv("SKOROZVON_CLIENT_ID")
    SKOROZVON_CLIENT_SECRET = os.getenv("SKOROZVON_CLIENT_SECRET")
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # App Configuration
    REPORT_TIME = os.getenv("REPORT_TIME", "18:00")  # Время отправки отчета
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Moscow")
