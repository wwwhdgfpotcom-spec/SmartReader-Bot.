import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo, MenuButtonWebApp
from aiogram.filters import Command

# مفتاح البوت (Token)
API_TOKEN = '8030434283:AAG4b_amj9uTU6a4rxxiN_Xv623NUsI7MHw'

# رابط موقعك
WEB_APP_URL = 'https://zippy-flan-60df29.netlify.app/'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# دالة لضبط زر القائمة ليفتح الموقع فوراً
async def set_menu_button():
    web_app = WebAppInfo(url=WEB_APP_URL)
    menu_button = MenuButtonWebApp(text="افتح الحاسبة", web_app=web_app)
    await bot.set_chat_menu_button(menu_button=menu_button)

# الترحيب بالمستخدم عند ضغط ستارت
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("أهلاً بك! يمكنك فتح الحاسبة من زر 'افتح الحاسبة' الموجود بجانب خانة الكتابة.")

# دالة التشغيل الرئيسية
async def main():
    await set_menu_button()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

