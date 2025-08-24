import os
import asyncio
from telethon.sessions import StringSession
from telethon import TelegramClient
from scripts import run_client, SESSIONS_DIR, API_ID, API_HASH

async def main():
    tasks = []
    for file in os.listdir(SESSIONS_DIR):
        if file.endswith(".session"):
            with open(os.path.join(SESSIONS_DIR, file), "r") as f:
                session_str = f.read().strip()
            client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await client.start()
            tasks.append(run_client(client))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())