#!/usr/bin/env bash
# ==============================================================================
# SCRIPT CẤU HÌNH NHANH TRÊN MÁY VPS TARGET (AGENTLESS / NO BOT DAEMON)
# Script này cài đặt 1 endpoint HTTP siêu nhẹ bằng Python3 (chạy như systemd service)
# hoặc Systemd Socket, kết hợp với Cloudflare Tunnel để nhận request an toàn
# ==============================================================================

set -e

PORT=${1:-9090}
SECRET_TOKEN=${2:-"$(openssl rand -hex 16)"}

echo "🚀 Bắt đầu thiết lập VPS Receiver (Port: $PORT)..."
echo "🔑 Secret Token của máy này: $SECRET_TOKEN"
echo ""

# 1. Tạo file receiver script bằng Python3 (không cần thư viện cài thêm)
cat << 'EOF' > /usr/local/bin/vps_receiver.py
#!/usr/bin/env python3
import http.server
import socketserver
import json
import subprocess
import os
import sys

PORT = int(os.environ.get("PORT", 9090))
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "")

class VPSHandler(http.server.BaseHTTPRequestHandler):
    def _authenticate(self):
        auth_header = self.headers.get("Authorization", "")
        expected = f"Bearer {SECRET_TOKEN}"
        if not SECRET_TOKEN or auth_header != expected:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
            return False
        return True

    def do_GET(self):
        if self.path == "/status":
            if not self._authenticate():
                return
            
            # Lấy thông tin tài nguyên máy chủ
            try:
                # CPU usage
                cpu = subprocess.getoutput("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'").strip()
                # RAM info
                ram_total = subprocess.getoutput("free -h | awk '/Mem:/ {print $2}'").strip()
                ram_used = subprocess.getoutput("free -h | awk '/Mem:/ {print $3}'").strip()
                ram_pct = subprocess.getoutput("free | awk '/Mem:/ {printf \"%.1f\", $3/$2 * 100}'").strip()
                # Disk info
                disk_total = subprocess.getoutput("df -h / | awk 'NR==2 {print $2}'").strip()
                disk_used = subprocess.getoutput("df -h / | awk 'NR==2 {print $3}'").strip()
                disk_pct = subprocess.getoutput("df -h / | awk 'NR==2 {print $5}'").replace('%','').strip()
                # Uptime & Load avg
                uptime = subprocess.getoutput("uptime -p").replace('up ', '').strip()
                load_avg = subprocess.getoutput("uptime | awk -F'load average:' '{print $2}'").strip()

                payload = {
                    "cpu": cpu,
                    "ram_total": ram_total,
                    "ram_used": ram_used,
                    "ram_percent": ram_pct,
                    "disk_total": disk_total,
                    "disk_used": disk_used,
                    "disk_percent": disk_pct,
                    "uptime": uptime,
                    "load_avg": load_avg
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if not self._authenticate():
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ""

        if self.path == "/exec":
            try:
                data = json.loads(body) if body else {}
                cmd = data.get("command", "")
                if not cmd:
                    self.send_response(400)
                    self.end_headers()
                    return

                # Thực thi câu lệnh Linux
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                output = res.stdout + res.stderr
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": res.returncode == 0,
                    "exit_code": res.returncode,
                    "output": output
                }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

        elif self.path == "/reboot":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Rebooting VPS..."}).encode('utf-8'))
            subprocess.Popen("sleep 1 && reboot", shell=True)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), VPSHandler) as httpd:
        print(f"VPS Micro Listener running on 127.0.0.1:{PORT}")
        httpd.serve_forever()
EOF

chmod +x /usr/local/bin/vps_receiver.py

# 2. Tạo file systemd service
cat << EOF > /etc/systemd/system/vps-receiver.service
[Unit]
Description=VPS Micro Receiver for Cloudflare Worker
After=network.target

[Service]
Type=simple
Environment=PORT=$PORT
Environment=SECRET_TOKEN=$SECRET_TOKEN
ExecStart=/usr/bin/python3 /usr/local/bin/vps_receiver.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now vps-receiver

echo "=========================================================="
echo "✅ Đã cài đặt xong VPS Receiver thành công!"
echo "📍 Service local: 127.0.0.1:$PORT"
echo "🔑 Token xác thực: $SECRET_TOKEN"
echo ""
echo "🔗 Bước tiếp theo: Cấu hình Cloudflare Tunnel (cloudflared)"
echo "   Trỏ Tunnel domain tới http://localhost:$PORT"
echo "=========================================================="
