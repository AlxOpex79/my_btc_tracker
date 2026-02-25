import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

# Настройки
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def get_rates():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uah&include_24hr_change=true"
        res = requests.get(url, timeout=10).json()
        btc = res['bitcoin']
        
        usd_p = btc['usd']
        uah_p = btc['uah']
        change = btc['usd_24h_change']
        
        emoji = "📈" if change > 0 else "📉"
        plus = "+" if change > 0 else ""
        
        return (
            f"📊 **Курс Bitcoin**\n"
            f"-------------------\n"
            f"💵 USD: ${usd_p:,}\n"
            f"₴ UAH: {uah_p:,} грн\n"
            f"-------------------\n"
            f"{emoji} Изм. за сутки: {plus}{change:.2f}%"
        )
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return "⚠️ Не удалось обновить курс."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    rates = get_rates()
    await message.answer(f"✅ Бот мониторинга активен!\n\n{rates}", parse_mode="Markdown")

async def send_scheduled_msg():
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, get_rates(), parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Ошибка рассылки: {e}")

async def main():
    # 07:00 UTC = 09:00 по нашему
    # 19:00 UTC = 21:00 по нашему
    scheduler.add_job(send_scheduled_msg, "cron", hour=7, minute=0)
    scheduler.add_job(send_scheduled_msg, "cron", hour=19, minute=0)
    
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
