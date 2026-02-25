import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests
import pytz

# Настройки
API_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
TIMEZONE = pytz.timezone('Europe/Kyiv')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

def get_rates():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uah&include_24hr_change=true"
        res = requests.get(url, timeout=10).json()
        btc = res['bitcoin']
        change = btc['usd_24h_change']
        emoji = "📈" if change > 0 else "📉"
        plus = "+" if change > 0 else ""
        return (
            f"📊 **Курс Bitcoin**\n"
            f"-------------------\n"
            f"💵 USD: ${btc['usd']:,}\n"
            f"₴ UAH: {btc['uah']:,} грн\n"
            f"-------------------\n"
            f"{emoji} Изм. за сутки: {plus}{change:.2f}%"
        )
    except:
        return "⚠️ Ошибка получения курса."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    rates = get_rates()
    # Бот сразу скажет ID чата, в котором его запустили
    await message.answer(
        f"✅ Бот запущен!\n"
        f"🆔 ID этого чата: `{message.chat.id}`\n\n"
        f"{rates}", 
        parse_mode="Markdown"
    )

async def send_scheduled_msg():
    if ADMIN_ID:
        try:
            await bot.send_message(ADMIN_ID, get_rates(), parse_mode="Markdown")
        except:
            pass

async def main():
    scheduler.add_job(send_scheduled_msg, "cron", hour=9, minute=0)
    scheduler.add_job(send_scheduled_msg, "cron", hour=21, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
