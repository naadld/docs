#!/usr/bin/env bash
# ==============================================================================
# SCRIPT TỰ ĐỘNG CÀI ĐẶT CÁC CÔNG CỤ MEDIA & TORRENT -> GOOGLE DRIVE TRÊN VPS
# ==============================================================================

set -e

echo "🚀 Đang cài đặt các thư viện phụ trợ (aria2, rclone, ffmpeg, yt-dlp, python3-pip)..."

# 1. Cài đặt các gói hệ thống
sudo apt-get update -y
sudo apt-get install -y aria2 rclone ffmpeg python3 python3-pip curl wget ca-certificates img2pdf poppler-utils || true

# 2. Cài đặt / Cập nhật yt-dlp
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# 3. Tạo script vps_media_worker.py xử lý Tải Video / MP3 / Format conversion
cat << 'EOF' > /usr/local/bin/vps_media_worker.py
#!/usr/bin/env python3
import sys
import argparse
import subprocess
import os
import json
import urllib.request

def send_telegram(chat_id, text, bot_token):
    if not bot_token:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Telegram notify error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--chat-id", required=True)
    args = parser.parse_args()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = args.chat_id
    action = args.action
    url = args.url

    output_dir = "/tmp/media_downloads"
    os.makedirs(output_dir, exist_ok=True)

    if action in ["youtube", "tiktok"]:
        cmd = f'yt-dlp -o "{output_dir}/%(title)s.%(ext)s" "{url}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            send_telegram(chat_id, f"✅ <b>Tải thành công [{action.upper()}]:</b>\n<code>{url}</code>", bot_token)
        else:
            send_telegram(chat_id, f"❌ <b>Lỗi tải [{action.upper()}]:</b> {res.stderr[:200]}", bot_token)

    elif action == "mp3":
        cmd = f'yt-dlp -x --audio-format mp3 -o "{output_dir}/%(title)s.%(ext)s" "{url}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            send_telegram(chat_id, f"🎧 <b>Tách MP3 thành công:</b>\n<code>{url}</code>", bot_token)
        else:
            send_telegram(chat_id, f"❌ <b>Lỗi tách MP3:</b> {res.stderr[:200]}", bot_token)

if __name__ == "__main__":
    main()
EOF

chmod +x /usr/local/bin/vps_media_worker.py

# 4. Tạo script vps_torrent_gdrive.py (Aria2 -> rclone Google Drive)
cat << 'EOF' > /usr/local/bin/vps_torrent_gdrive.py
#!/usr/bin/env python3
import sys
import argparse
import subprocess
import os
import json
import urllib.request
import time

def send_telegram(chat_id, text, bot_token):
    if not bot_token:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Telegram notify error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--magnet", required=True)
    parser.add_argument("--chat-id", required=True)
    args = parser.parse_args()

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = args.chat_id
    magnet = args.magnet

    download_dir = f"/tmp/torrent_{int(time.time())}"
    os.makedirs(download_dir, exist_ok=True)

    send_telegram(chat_id, "🧲 <b>Đang bắt đầu tải Torrent về VPS...</b>", bot_token)

    # Tải qua aria2c
    cmd_aria2 = f'aria2c --dir="{download_dir}" --seed-time=0 --max-connection-per-server=8 "{magnet}"'
    res = subprocess.run(cmd_aria2, shell=True, capture_output=True, text=True)

    if res.returncode != 0:
        send_telegram(chat_id, f"❌ <b>Lỗi tải Torrent:</b>\n<pre>{res.stderr[:300]}</pre>", bot_token)
        return

    send_telegram(chat_id, "☁️ <b>Tải Torrent xong! Đang đẩy trực tiếp lên Google Drive...</b>", bot_token)

    # Push lên Google Drive qua rclone remote (tên remote mặc định: gdrive)
    cmd_rclone = f'rclone move "{download_dir}" gdrive:TelegramDownloads/ --transfers 4 -v'
    res_rclone = subprocess.run(cmd_rclone, shell=True, capture_output=True, text=True)

    if res_rclone.returncode == 0:
        send_telegram(chat_id, "🎉 <b>Hoàn tất 100%!</b>\nFile Torrent đã nằm gọn trong thư mục <code>TelegramDownloads</code> trên Google Drive của bạn.", bot_token)
    else:
        send_telegram(chat_id, f"❌ <b>Lỗi upload lên Google Drive:</b>\n<pre>{res_rclone.stderr[:300]}</pre>", bot_token)

    # Dọn dẹp folder tạm
    subprocess.run(f'rm -rf "{download_dir}"', shell=True)

if __name__ == "__main__":
    main()
EOF

chmod +x /usr/local/bin/vps_torrent_gdrive.py

echo "=========================================================="
echo "✅ Đã cài đặt xong Media Tools & Torrent->GDrive Engine!"
echo "=========================================================="
