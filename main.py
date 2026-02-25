import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

# Берем настройки из переменных Railway
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def get_rates():
    try:
        # Запрашиваем цену и изменение за последние 24 часа
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uah&include_24hr_change=true"
        res = requests.get(url, timeout=10).json()
        
        btc_data = res['bitcoin']
        usd_price = btc_data['usd']
        uah_price = btc_data['uah']
        change = btc_data['usd_24h_change']
        
        # Определяем статус: рост или падение
        if change > 0:
            status = f"📈 Рост: +{change:.2f}%"
        elif change < 0:
            status = f"📉 Падение: {change:.2f}%"
        else:
            status = "↔️ Без изменений"
            
        text = (
            f"📊 **Курс Bitcoin**\n"
            f"-------------------\n"
            f"💵 USD: ${usd_price:,}\n"
            f"₴ UAH: {uah_price:,} грн\n"
            f"-------------------\n"
            f"{status}"
        )
        return text
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return "⚠️ Не удалось получить данные о курсе."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # При старте бот сразу выдает текущий курс и подтверждает ID
    rates = get_rates()
    await message.answer(
        f"Привет, Алексей! Бот мониторинга запущен.\n\n"
        f"Твой ID: `{message.from_user.id}`\n\n"
        f"{rates}",
        parse_mode="Markdown"
    )

async def send_scheduled_msg():
    if ADMIN_ID:
        rates = get_rates()
        try:
            await bot.send_message(ADMIN_ID, rates, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Ошибка отправки: {e}")

async def main():
    # Настройка рассылки (09:00 и 21:00 по времени сервера)
    scheduler.add_job(send_scheduled_msg, "cron", hour=9, minute=0)
    scheduler.add_job(send_scheduled_msg, "cron", hour=21, minute=0)
    
    scheduler.start()
    
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
