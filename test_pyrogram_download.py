import asyncio, os, sys
from pyrogram import Client

api_id = 2755609
api_hash = "1b9ba4527fadc9cebfd2010a438a4f90"
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8956702590:AAG-Md8W19LU5hjGYpolfA6uFHbsJixHgmo")
chat_id = -1004329103449
target_msg_id = 157
input_file = "work/test_download.pdf"

os.makedirs("work", exist_ok=True)

async def download_large():
    print("Initializing Pyrogram Client...")
    app = Client("large_file_engine", api_id=api_id, api_hash=api_hash, bot_token=bot_token, in_memory=True)
    async with app:
        print(f"Fetching message {target_msg_id} from {chat_id}...")
        msg = await app.get_messages(chat_id, target_msg_id)
        if not msg:
            print("Message not found!")
            return
        print("Starting download...")
        res = await app.download_media(msg, file_name=input_file)
        print("Download result:", res)

try:
    asyncio.run(download_large())
except Exception as e:
    print("Exception:", e)

