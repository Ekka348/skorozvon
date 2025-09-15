import requests
import schedule
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Any

from app.config import Config
from app.utils import get_skorozvon_token, send_to_telegram

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_calls_report(access_token: str, start_time: int, end_time: int) -> Dict[str, Any]:
    """Получение отчета о звонках из Skorozvon"""
    report_url = f"{Config.SKOROZVON_API_URL}/api/reports/calls_total.json"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    report_payload = {
        "start_time": start_time,
        "end_time": end_time,
        "length": 1000,
        "page": 1,
        "filter": {
            "types": "all",
            "users_ids": "all",
            "scenarios_ids": "all",
            "results_ids": "all"
        }
    }
    
    try:
        response = requests.post(report_url, json=report_payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка при получении отчета: {e}")
        return None

def calculate_operator_stats(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Расчет статистики по операторам"""
    operator_stats = defaultdict(lambda: {
        'name': 'Неизвестно',
        'total_calls': 0,
        'successful_calls': 0,
        'total_duration': 0,
        'call_types': defaultdict(int)
    })
    
    if not report_data or 'data' not in report_data:
        return operator_stats
    
    for call in report_data['data']:
        user_info = call.get('user', {})
        user_id = user_info.get('id')
        user_name = user_info.get('name', 'Неизвестно')
        
        if not user_id:
            continue
            
        operator = operator_stats[user_id]
        operator['name'] = user_name
        operator['total_calls'] += 1
        operator['total_duration'] += call.get('duration', 0)
        
        # Считаем успешные звонки
        result_group = call.get('scenario_result_group', {})
        if result_group and 'Успешн' in result_group.get('title', ''):
            operator['successful_calls'] += 1
        
        # Считаем типы звонков
        call_type = call.get('call_type_code', 'unknown')
        operator['call_types'][call_type] += 1
    
    return operator_stats

def format_stats_message(operator_stats: Dict[str, Any], date_period: str) -> str:
    """Форматирование сообщения для Telegram"""
    if not operator_stats:
        return "📊 Нет данных о звонках за указанный период"
    
    message = f"📊 <b>Статистика операторов за {date_period}</b>\n\n"
    
    for user_id, stats in operator_stats.items():
        if stats['total_calls'] == 0:
            continue
            
        avg_duration = stats['total_duration'] / stats['total_calls']
        success_rate = (stats['successful_calls'] / stats['total_calls'] * 100) if stats['total_calls'] > 0 else 0
        
        message += f"👤 <b>{stats['name']}</b>:\n"
        message += f"   • 📞 Всего звонков: {stats['total_calls']}\n"
        message += f"   • ✅ Успешных: {stats['successful_calls']} ({success_rate:.1f}%)\n"
        message += f"   • ⏱️ Общее время: {stats['total_duration']//60} мин.\n"
        message += f"   • 🕐 Среднее время: {avg_duration:.1f} сек.\n"
        message += f"   • 🔄 Исходящие: {stats['call_types'].get('outgoing', 0)}\n"
        message += f"   • 📥 Входящие: {stats['call_types'].get('incoming', 0)}\n\n"
    
    return message

def generate_daily_report():
    """Генерация ежедневного отчета"""
    logger.info("🔄 Запуск генерации ежедневного отчета...")
    
    access_token = get_skorozvon_token()
    if not access_token:
        logger.error("❌ Не удалось получить токен доступа")
        return
    
    # Получаем данные за вчерашний день
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    start_time = int(yesterday.replace(hour=0, minute=0, second=0).timestamp())
    end_time = int(yesterday.replace(hour=23, minute=59, second=59).timestamp())
    date_str = yesterday.strftime("%d.%m.%Y")
    
    logger.info(f"📊 Запрашиваем данные за {date_str}...")
    report_data = get_calls_report(access_token, start_time, end_time)
    
    if not report_data:
        logger.error("❌ Не удалось получить данные отчета")
        return
    
    logger.info(f"✅ Получено {len(report_data.get('data', []))} записей")
    
    # Анализируем данные
    operator_stats = calculate_operator_stats(report_data)
    
    # Формируем сообщение
    message = format_stats_message(operator_stats, date_str)
    
    # Отправляем в Telegram
    if send_to_telegram(message):
        logger.info("✅ Отчет отправлен в Telegram")
    else:
        logger.error("❌ Ошибка отправки отчета в Telegram")

def main():
    """Основная функция"""
    logger.info("🚀 Skorozvon Telegram Bot запущен")
    
    # Планировщик для ежедневной отправки
    schedule.every().day.at(Config.REPORT_TIME).do(generate_daily_report)
    
    # Также можно запустить сразу для теста
    generate_daily_report()
    
    # Бесконечный цикл для планировщика
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
