import os
import asyncio
import logging
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Настройка логирования, чтобы видеть активность в консоли Render
logging.basicConfig(level=logging.INFO)

# Берем данные из Environment Variables на Render
API_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

# Функция получения курса Bitcoin
def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        logging.error(f"Ошибка получения курса: {e}")
        return None

# Функция отправки сообщения по расписанию
async def send_price_update():
    price = get_btc_price()
    if price:
        message = f"📊 Курс Bitcoin на {datetime.now().strftime('%H:%M')}:\n💰 ${price:,}"
        # Отправляем и тебе, и в логи Render для контроля
        await bot.send_message(chat_id=USER_ID, text=message)
        logging.info(f"Курс отправлен пользователю {USER_ID}")

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет! Я работаю. Буду присылать курс BTC в 09:00 и 21:00 по Киеву.\n\nТвой ID: {message.from_user.id}")
    logging.info(f"Получена команда /start от {message.from_user.id}")

# Простейший веб-сервер для Render (чтобы он не усыплял сервис)
async def handle(request):
    return web.Response(text="Bot is alive and kicking!")

app = web.Application()
app.router.add_get("/", handle)

async def main():
    # Настройка расписания рассылки
    scheduler.add_job(send_price_update, 'cron', hour=9, minute=0)
    scheduler.add_job(send_price_update, 'cron', hour=21, minute=0)
    scheduler.start()

    # Запуск веб-сервера для "будильника" (порт 10000 по умолчанию для Render)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logging.info("Бот запущен и ждет расписания...")
    
    # Запуск прослушивания сообщений Telegram
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
