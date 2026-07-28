#!/usr/bin/env python3
import json
import subprocess
import urllib.request
import os
import html

BOT_TOKEN = "8027319967:AAERPtaSTFjxtPjaOx3dZ00__MoD_XVIQc8"
CHAT_ID = "-1004329103449"
THREAD_ID = 2

def render_progress_bar(percent_num: float, length: int = 10) -> str:
    filled_len = min(length, max(0, int(round((percent_num / 100.0) * length))))
    empty_len = length - filled_len
    return "[" + ("█" * filled_len) + ("░" * empty_len) + "]"

def clean_str(val) -> str:
    return html.escape(str(val).strip())

def get_sys_stats():
    uptime = subprocess.getoutput("uptime -p").replace("up ", "").strip()
    try:
        cpu = float(subprocess.getoutput("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").strip() or 0)
    except:
        cpu = 0.0
    ram_total = subprocess.getoutput("free -h | awk '/Mem:/ {print $2}'").strip()
    ram_used = subprocess.getoutput("free -h | awk '/Mem:/ {print $3}'").strip()
    ram_free = subprocess.getoutput("free -h | awk '/Mem:/ {print $4}'").strip()
    try:
        ram_pct = float(subprocess.getoutput("free | awk '/Mem:/ {printf \"%.1f\", $3/$2 * 100}'").strip() or 0)
    except:
        ram_pct = 0.0
    swap_total = subprocess.getoutput("free -h | awk '/Swap:/ {print $2}'").strip()
    swap_used = subprocess.getoutput("free -h | awk '/Swap:/ {print $3}'").strip()
    disk_total = subprocess.getoutput("df -h / | awk 'NR==2 {print $2}'").strip()
    disk_used = subprocess.getoutput("df -h / | awk 'NR==2 {print $3}'").strip()
    try:
        disk_pct = float(subprocess.getoutput("df / | awk 'NR==2 {printf \"%.1f\", $3/$2 * 100}'").strip() or 0)
    except:
        disk_pct = 0.0
    
    docker_containers = subprocess.getoutput("docker ps --format '{{.Names}}' 2>/dev/null | tr '\n' ', ' | sed 's/,$//'").strip()
    if not docker_containers:
        docker_containers = "None active"

    bar_cpu = render_progress_bar(cpu, 10)
    bar_ram = render_progress_bar(ram_pct, 10)
    bar_disk = render_progress_bar(disk_pct, 10)

    msg = f"""📊 <b>MONITOR SYSTEM [vpsg16gb]</b>

⏱️ Uptime: <code>{clean_str(uptime)}</code>
🔥 CPU Usage: <code>{bar_cpu} {cpu:.1f}%</code>
🧠 RAM Usage: <b>{clean_str(ram_used)} / {clean_str(ram_total)}</b> (Free: <code>{clean_str(ram_free)}</code>)
   <code>{bar_ram} {ram_pct:.1f}%</code>
💾 SWAP: <code>{clean_str(swap_used)} / {clean_str(swap_total)}</code>
💿 Disk /: <b>{clean_str(disk_used)} / {clean_str(disk_total)}</b> <code>{bar_disk} {disk_pct:.1f}%</code>
🐳 Docker: <code>{clean_str(docker_containers)}</code>""".strip()
    return msg

def main():
    text = get_sys_stats()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": THREAD_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get("ok"):
                print("✅ Successfully sent vpsg16gb stats report to Topic 2!")
            else:
                print(f"❌ Telegram API Error: {data}")
    except Exception as e:
        print(f"❌ Failed to send message: {e}")

if __name__ == "__main__":
    main()
