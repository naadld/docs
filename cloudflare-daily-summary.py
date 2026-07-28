#!/usr/bin/env python3
import json
import urllib.request
import datetime

BOT_TOKEN = "8956702590:AAGwVRp1VsYm37uDvo50_yczDhkROrjoL6w"
CHAT_ID = "-1004329103449"
# General Topic (Topic 1) omits message_thread_id in Telegram payload

CF_TOKEN = "cfut_zbMaTDEhNEz1zQApcqU3sE2Y1s35DnrTS50BxrC2d4941a88"
ACCOUNT_ID = "ef0cdb72b520ceb69113c4e6f3705024"
FREE_LIMIT = 100000

def render_progress_bar(percent_num: float, length: int = 10) -> str:
    filled_len = min(length, max(0, int(round((percent_num / 100.0) * length))))
    empty_len = length - filled_len
    return "[" + ("█" * filled_len) + ("░" * empty_len) + "]"

def fetch_cf_analytics():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    query = f"""query {{ viewer {{ accounts(filter: {{accountTag: "{ACCOUNT_ID}"}}) {{ workersInvocationsAdaptive(limit: 10, filter: {{date_geq: "{today_str}"}}) {{ sum {{ requests }} }} }} }} }}"""
    
    url = "https://api.cloudflare.com/client/v4/graphql"
    payload = json.dumps({"query": query}).encode('utf-8')
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            accounts = data.get("data", {}).get("viewer", {}).get("accounts", [])
            req_today = 0
            if accounts:
                invocations = accounts[0].get("workersInvocationsAdaptive", [])
                for item in invocations:
                    req_today += item.get("sum", {}).get("requests", 0)
            return req_today
    except Exception as e:
        print(f"Error fetching CF analytics: {e}")
        return 0

def main():
    req_used = fetch_cf_analytics()
    remaining = max(0, FREE_LIMIT - req_used)
    pct = (req_used / FREE_LIMIT) * 100.0
    bar = render_progress_bar(pct, 10)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""📊 <b>CLOUDFLARE DAILY USAGE SUMMARY (Pre-Reset 06:50 AM)</b>

🗓️ <i>Cycle Date: {now_str} (GMT+7)</i>
🌐 Account: <a href="https://dash.cloudflare.com/{ACCOUNT_ID}/workers-and-pages">aleron</a>
⚡ Free Tier Quota: <b>{FREE_LIMIT:,} / day</b>
📈 Total Requests Used Today: <b>{req_used:,}</b> requests
📉 Remaining Quota Before Reset: <b>{remaining:,}</b> requests

📊 Final Usage: <code>{bar} {pct:.2f}%</code>

⏳ <i>Daily quota resets in 10 minutes at 07:00 AM GMT+7.</i>"""

    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    tg_payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": report,
        "parse_mode": "HTML"
    }).encode('utf-8')

    tg_req = urllib.request.Request(tg_url, data=tg_payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(tg_req) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            if res_data.get("ok"):
                print("✅ Successfully sent Cloudflare Daily Usage Summary to Topic 1!")
            else:
                print(f"❌ Telegram API Error: {res_data}")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

if __name__ == "__main__":
    main()
