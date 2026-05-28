import asyncio
import os
import random
import google.generativeai as genai
from telethon import TelegramClient, functions, types

# --- الدوال الثلاث للتحكم الذكي ---
def get_random_delay():
    return random.randint(5, 20)

# --- دالة الضغط على زر بناءً على النص ---
async def click_button_by_text(client, message, target_text):
    if not message.reply_markup: return False
    for row in message.reply_markup.rows:
        for button in row.buttons:
            if target_text in button.text:
                await client(functions.messages.GetBotCallbackAnswerRequest(
                    peer=message.chat_id,
                    msg_id=message.id,
                    data=button.data
                ))
                return True
    return False

# --- دالة حل الكابتشا ---
async def solve_captcha_with_gemini(client, message, gemini_key):
    path = await client.download_media(message.photo)
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    sample_file = genai.upload_file(path=path)
    response = model.generate_content([sample_file, "استخرج الرقم من الكابتشا، فقط الرقم."])
    os.remove(path)
    return response.text.strip()

# --- المحرك الرئيسي ---
async def run_automation_engine(phone, api_id, api_hash, gemini_key, bot_instance, chat_id, target_count=250):
    session_name = f"session_{phone}"
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone=phone)
    bot_username = '@gram_piarbot' # ضع هنا اسم البوت الحقيقي

    try:
        await client.send_message(bot_username, '/start')
        await asyncio.sleep(2)
        
        for i in range(target_count):
            # 1. طلب "اشتراك"
            # (نفرض أننا حصلنا على رسالة المهمة)
            async for message in client.iter_messages(bot_username, limit=1):
                if await click_button_by_text(client, message, "اشتراك"):
                    await asyncio.sleep(get_random_delay())
                    
                    # 2. الفحص الميداني للقناة
                    async for dialog in client.iter_dialogs(limit=5):
                        if dialog.is_channel:
                            channel = dialog.entity
                            # شرط: هل تتطلب طلب انضمام؟
                            if getattr(channel, 'join_request', False):
                                await client(functions.channels.LeaveChannelRequest(channel))
                                break
                            
                            # كتم القناة
                            await client(functions.channels.EditBannedRequest(channel, None, until_date=None, view_messages=True))
                            break

                    # 3. العودة والضغط على "فحص"
                    if await click_button_by_text(client, message, "فحص"):
                        await client.send_message('me', f"تم الاشتراك في العملية {i+1}")
                    else:
                        # في حال ظهرت كابتشا بدلاً من "فحص"
                        captcha_code = await solve_captcha_with_gemini(client, message, gemini_key)
                        await client.send_message(bot_username, captcha_code)
            
            await asyncio.sleep(get_random_delay())

    finally:
        await client.disconnect()
        if os.path.exists(f"{session_name}.session"):
            os.remove(f"{session_name}.session")
