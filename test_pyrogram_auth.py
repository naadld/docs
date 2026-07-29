import asyncio, os
from pyrogram import Client
api_id = 611335
api_hash = "d524b507821326ef78b2352d2fd01829"
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8956702590:AAG-Md8W19LU5hjGYpolfA6uFHbsJixHgmo")

async def main():
    app = Client("test_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token, in_memory=True)
    try:
        await app.start()
        print("Connected OK")
        await app.stop()
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
