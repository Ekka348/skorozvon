import requests
import logging
from app.config import Config

logger = logging.getLogger(__name__)

def get_skorozvon_token():
    """Получение токена доступа Skorozvon"""
    auth_url = f"{Config.SKOROZVON_API_URL}/oauth/token"
    auth_data = {
        "grant_type": "password",
        "username": Config.SKOROZVON_USERNAME,
        "api_key": Config.SKOROZVON_API_KEY,
        "client_id": Config.SKOROZVON_CLIENT_ID,
        "client_secret": Config.SKOROZVON_CLIENT_SECRET
    }
    
    try:
        response = requests.post(auth_url, data=auth_data, timeout=10)
        response.raise_for_status()
        token_data = response.json()
        return token_data['access_token']
    except Exception as e:
        logger.error(f"Ошибка при получении токена: {e}")
        return None

def send_to_telegram(message: str) -> bool:
    """Отправка сообщения в Telegram"""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        logger.error("Не настроен Telegram бот")
        return False
    
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        return False
