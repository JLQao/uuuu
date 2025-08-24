import os
import json
import asyncio
from datetime import datetime
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "your_api_hash")

# المطور الأساسي (ضع الـ id الخاص بك هنا)
MAIN_DEVS = [123456789]

# ملف الحسابات المسموح بها
ALLOWED_FILE = os.path.join(os.path.dirname(__file__), "allowed.json")

if os.path.exists(ALLOWED_FILE):
    with open(ALLOWED_FILE, "r") as f:
        ALLOWED_USERS = json.load(f)
else:
    ALLOWED_USERS = []
    with open(ALLOWED_FILE, "w") as f:
        json.dump(ALLOWED_USERS, f)

# مجلد الجلسات
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)


def is_allowed(user_id: int) -> bool:
    """يتأكد إذا المستخدم مصرح له أو مطور أساسي"""
    return user_id in MAIN_DEVS or user_id in ALLOWED_USERS


async def run_client(client: TelegramClient):
    me = await client.get_me()
    print(f"✅ تشغيل جلسة: {me.username or me.id}")

    # أمر التفعيل
    @client.on(events.NewMessage(pattern=r"^\.تفعيل$"))
    async def _(event):
        if is_allowed(event.sender_id):
            await event.reply("✅ تم تفعيل الحساب بنجاح.")
        else:
            await event.reply("⚠️ حسابك غير مصرح به. راسل المطور لإضافتك.")

    # أمر إضافة مستخدم
    @client.on(events.NewMessage(pattern=r"^\.اضافه\+(\d+)$"))
    async def _(event):
        if event.sender_id not in MAIN_DEVS:
            return await event.reply("⚠️ هذا الأمر للمطور فقط.")
        new_id = int(event.pattern_match.group(1))
        if new_id not in ALLOWED_USERS:
            ALLOWED_USERS.append(new_id)
            with open(ALLOWED_FILE, "w") as f:
                json.dump(ALLOWED_USERS, f)
            await event.reply(f"✅ تم إضافة الحساب {new_id} إلى قائمة المصرح لهم.")
        else:
            await event.reply("ℹ️ الحساب موجود بالفعل في القائمة.")

    # باقي الأوامر تعمل فقط للمسموح لهم
    @client.on(events.NewMessage(pattern=r"^\.حاله$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        await event.reply("📊 المحاولات: (هنا تحط الكاونتر)")

    @client.on(events.NewMessage(pattern=r"^\.الصيد$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        await event.reply("📌 انت الان في قسم الصيد . ارسل النموذج لبدء الفحص...")

    @client.on(events.NewMessage(pattern=r"^\.صيد\+(.+)$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        shape = event.pattern_match.group(1)
        await event.reply(f"⏳ بدء الصيد للشكل: {shape}")

    @client.on(events.NewMessage(pattern=r"^\.ايقاف الصيد$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        await event.reply("🛑 تم إيقاف الصيد.")

    @client.on(events.NewMessage(pattern=r"^\.انشاء\+(\d+)$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        num = int(event.pattern_match.group(1))
        for i in range(num):
            group = await client(functions.messages.CreateChatRequest(
                users=[],
                title=f"قروب التخزين {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ))
            chat_id = group.chats[0].id
            for j in range(10):
                await client.send_message(chat_id, f"تم انشاء هاذ القروب تلقائي من قبل سورس اوريون مطور السورس @seesr {j+1}")
        await event.reply(f"✅ تم إنشاء {num} مجموعات مع 10 رسائل في كل مجموعة.")

    @client.on(events.NewMessage(pattern=r"^\.ا$"))
    async def _(event):
        if not is_allowed(event.sender_id):
            return
        me = await client.get_me()
        info = (
            f"👤 اليوزر: @{me.username}\n"
            f"🆔 الايدي: {me.id}\n"
            f"📅 تاريخ الإنشاء: {me.date}\n"
            f"💬 عدد الرسائل: {await client.get_messages(event.chat_id, limit=0).total}"
        )
        if me.photo:
            await event.reply(info, file=await client.download_profile_photo(me))
        else:
            await event.reply(info)