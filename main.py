import os
import asyncio
from aiogram import Bot, Dispatcher
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

# Берем данные из настроек Render (Environment Variables)
API_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Kyiv")

# Функция получения курса
def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        data = requests.get(url).json()
        return data['bitcoin']['usd']
    except: return None

# Сама рассылка
async def send_price_update():
    price = get_btc_price()
    if price:
        await bot.send_message(USER_ID, f"📊 Курс BTC: ${price:,}")

# Простейший веб-сервер для Render
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

async def main():
    # Настройка расписания
    scheduler.add_job(send_price_update, 'cron', hour=9, minute=0)
    scheduler.add_job(send_price_update, 'cron', hour=21, minute=0)
    scheduler.start()

    # Запуск веб-сервера и бота одновременно
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
