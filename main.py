import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

# Берем токен из переменных окружения (настроим на хостинге)
API_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

def get_crypto_rates():
    try:
        # Берем данные по BTC в USD и UAH
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,uah"
        res = requests.get(url, timeout=10).json()
        btc_usd = res['bitcoin']['usd']
        btc_uah = res['bitcoin']['uah']
        return f"₿ BTC: ${btc_usd:,}\n₴ BTC: {btc_uah:,} UAH"
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        return "⚠️ Не удалось получить актуальный курс."

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Бот пришлет вам ваш ID — он пригодится для настройки рассылки
    your_id = message.from_user.id
    await message.answer(f"Привет, Алексей! Ваш ID: `{your_id}`\n\nТекущий курс:\n{get_crypto_rates()}\n\nСкопируйте ID и добавьте его в настройки хостинга (ADMIN_ID).")

async def send_scheduled_msg(chat_id):
    rates = get_crypto_rates()
    await bot.send_message(chat_id, f"📢 Плановое обновление курса:\n\n{rates}")

async def main():
    # Настройка рассылки (пример на ваш ID, который мы укажем в настройках)
    admin_id = os.getenv('ADMIN_ID')
    if admin_id:
        scheduler.add_job(send_scheduled_msg, "cron", hour=9, minute=0, args=[admin_id])
        scheduler.add_job(send_scheduled_msg, "cron", hour=21, minute=0, args=[admin_id])
    
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
