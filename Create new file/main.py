import os
import asyncio
from telethon import TelegramClient, events, Button
from task_engine import run_automation_engine 

# جلب الإعدادات من متغيرات البيئة
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECRET_CODE = os.environ.get("SECRET_CODE")

# إنشاء العميل (البوت)
bot = TelegramClient('bot_gateway', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# تخزين مؤقت لحالة المستخدم والمهام
user_session = {"authorized": False, "task": None}

@bot.on(events.NewMessage(pattern=f"^{SECRET_CODE}$"))
async def authorize(event):
    user_session["authorized"] = True
    await event.respond("تم التحقق بنجاح. اختر العملية:", buttons=[
        [Button.text("تشغيل المحرك"), Button.text("إيقاف المحرك")]
    ])

@bot.on(events.NewMessage(pattern="تشغيل المحرك"))
async def start_engine(event):
    if not user_session["authorized"]:
        return
    
    if user_session["task"] and not user_session["task"].done():
        await event.respond("المحرك يعمل بالفعل!")
        return

    async with bot.conversation(event.chat_id) as conv:
        # 1. طلب رقم الهاتف
        await conv.send_message("يرجى إدخال رقم هاتفك (مع رمز الدولة):")
        phone = (await conv.get_response()).text
        
        # 2. طلب مفتاح Gemini API
        await conv.send_message("يرجى إدخال مفتاح Gemini API الخاص بك:")
        gemini_key = (await conv.get_response()).text
        
        await event.respond("جاري تهيئة الاتصال بالمحرك...")
        
        # تشغيل المحرك كـ Task منفصل وتمرير مفتاح Gemini الجديد
        task = asyncio.create_task(run_automation_engine(
            phone, API_ID, API_HASH, gemini_key, bot, event.chat_id
        ))
        user_session["task"] = task
        await event.respond("تم تشغيل المحرك بنجاح باستخدام المفتاح المعطى.")

@bot.on(events.NewMessage(pattern="إيقاف المحرك"))
async def stop_engine(event):
    if user_session["task"]:
        user_session["task"].cancel()
        user_session["task"] = None
        await event.respond("تم إيقاف المحرك وإغلاق الجلسة.")
    else:
        await event.respond("لا توجد مهمة تعمل حالياً.")

print("البوت يعمل الآن في وضع الاستعداد...")
bot.run_until_disconnected()
