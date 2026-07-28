#!/usr/bin/env python3
import json
import urllib.request
import sys
import datetime
import html

BOT_TOKEN = "8027319967:AAERPtaSTFjxtPjaOx3dZ00__MoD_XVIQc8"
CHAT_ID = "-1004329103449"
THREAD_ID = 2  # Topic 2 (vpsg16gb)

def notify(action_title: str, target_name: str, status_detail: str = "Completed successfully"):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    msg = f"""📢 <b>SYSTEM ACTION REPORT [vpsg16gb]</b>

⚙️ <b>Action:</b> <code>{html.escape(action_title)}</code>
📦 <b>Target App/Container:</b> <code>{html.escape(target_name)}</code>
⏱️ <b>Timestamp:</b> <code>{now_str} (GMT+7)</code>
📝 <b>Status:</b> <b>{html.escape(status_detail)}</b>

✅ <i>Live system event notification recorded.</i>"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": THREAD_ID,
        "text": msg,
        "parse_mode": "HTML"
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("ok"):
                print(f"✅ Notification sent to Topic 2: {action_title} ({target_name})")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        action = sys.argv[1]
        target = sys.argv[2]
        detail = sys.argv[3] if len(sys.argv) >= 4 else "Completed successfully"
        notify(action, target, detail)
    else:
        print("Usage: python3 vpsg16gb-notify.py <Action> <Target> [Detail]")
