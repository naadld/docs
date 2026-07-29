import asyncio, os
from pyrogram import Client

api_id = 2755609
api_hash = "1b9ba4527fadc9cebfd2010a438a4f90"
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8956702590:AAG-Md8W19LU5hjGYpolfA6uFHbsJixHgmo")
file_id = "BQACAgUAAyEFAAMBAgjgWQADfmpolVoMyqo10tbbe1XjcYYX4J5eAAJCGQACfFLoVIAF2ky9w4A1PQQ"
input_file = "work/test_download2.pdf"

os.makedirs("work", exist_ok=True)

async def main():
    app = Client("test_fileid", api_id=api_id, api_hash=api_hash, bot_token=bot_token, in_memory=True)
    async with app:
        print("Downloading via file_id...")
        res = await app.download_media(file_id, file_name=input_file)
        print("Result:", res)

asyncio.run(main())
