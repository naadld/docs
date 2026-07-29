import requests, os
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8956702590:AAG-Md8W19LU5hjGYpolfA6uFHbsJixHgmo")
res = requests.get(f"http://localhost:8081/bot{bot_token}/getMe").json()
print("getMe:", res)
