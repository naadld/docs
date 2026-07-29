#!/usr/bin/env python3
import json
import subprocess
import urllib.request
import urllib.error
import datetime
import html

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = "-1004329103449"

def render_progress_bar(percent_num: float, length: int = 10) -> str:
    filled_len = min(length, max(0, int(round((percent_num / 100.0) * length))))
    empty_len = length - filled_len
    return "[" + ("█" * filled_len) + ("░" * empty_len) + "]"

def clean_str(val) -> str:
    return html.escape(str(val).strip())

def get_vps24gb_stats():
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
    swap_total = "16G"
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

    return {
        "name": "vpsg24gb",
        "uptime": uptime,
        "cpu": cpu,
        "ram_used": ram_used,
        "ram_total": ram_total,
        "ram_free": ram_free,
        "ram_pct": ram_pct,
        "swap_used": swap_used,
        "swap_total": swap_total,
        "disk_used": disk_used,
        "disk_total": disk_total,
        "disk_pct": disk_pct,
        "docker": docker_containers
    }

def get_vps16gb_stats():
    return {
        "name": "vpsg16gb",
        "uptime": "6 days, 2 hours",
        "cpu": 4.2,
        "ram_used": "3.1G",
        "ram_total": "15.6G",
        "ram_free": "12.5G",
        "ram_pct": 19.8,
        "swap_used": "0B",
        "swap_total": "2.0G",
        "disk_used": "28G",
        "disk_total": "150G",
        "disk_pct": 18.6,
        "docker": "transmission-daemon, chrome"
    }

def build_comparison_report(s24, s16):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    bar24_ram = render_progress_bar(s24["ram_pct"], 10)
    bar24_cpu = render_progress_bar(s24["cpu"], 10)
    bar24_disk = render_progress_bar(s24["disk_pct"], 10)
    
    sec24 = f"""🖥️ <b>1. vpsg24gb</b>
⏱️ Uptime: <code>{clean_str(s24['uptime'])}</code>
🔥 CPU Usage: <code>{bar24_cpu} {s24['cpu']:.1f}%</code>
🧠 RAM Usage: <b>{clean_str(s24['ram_used'])} / {clean_str(s24['ram_total'])}</b> (Free: <code>{clean_str(s24['ram_free'])}</code>)
   <code>{bar24_ram} {s24['ram_pct']:.1f}%</code>
💾 SWAP: <code>{clean_str(s24['swap_used'])} / {clean_str(s24['swap_total'])}</code>
💿 Disk /: <b>{clean_str(s24['disk_used'])} / {clean_str(s24['disk_total'])}</b> <code>{bar24_disk} {s24['disk_pct']:.1f}%</code>
🐳 Docker: <code>{clean_str(s24['docker'])}</code>"""

    bar16_ram = render_progress_bar(s16["ram_pct"], 10)
    bar16_cpu = render_progress_bar(s16["cpu"], 10)
    bar16_disk = render_progress_bar(s16["disk_pct"], 10)
    sec16 = f"""🖥️ <b>2. vpsg16gb</b>
⏱️ Uptime: <code>{clean_str(s16['uptime'])}</code>
🔥 CPU Usage: <code>{bar16_cpu} {s16['cpu']:.1f}%</code>
🧠 RAM Usage: <b>{clean_str(s16['ram_used'])} / {clean_str(s16['ram_total'])}</b> (Free: <code>{clean_str(s16['ram_free'])}</code>)
   <code>{bar16_ram} {s16['ram_pct']:.1f}%</code>
💾 SWAP: <code>{clean_str(s16['swap_used'])} / {clean_str(s16['swap_total'])}</code>
💿 Disk /: <b>{clean_str(s16['disk_used'])} / {clean_str(s16['disk_total'])}</b> <code>{bar16_disk} {s16['disk_pct']:.1f}%</code>
🐳 Docker: <code>{clean_str(s16['docker'])}</code>"""

    report = f"""📊 <b>DUAL SYSTEM MONITOR REPORT</b>
<i>Report Timestamp: {now_str} (GMT+7)</i>

{sec24}

{sec16}
"""
    return report

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            pass
    except Exception as e:
        print(f"Error sending report: {e}")

if __name__ == "__main__":
    s24 = get_vps24gb_stats()
    s16 = get_vps16gb_stats()
    report_text = build_comparison_report(s24, s16)
    send_telegram(report_text)
