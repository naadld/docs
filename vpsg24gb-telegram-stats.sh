#!/usr/bin/env bash
# ==============================================================================
# SCRIPT KIỂM TRA & BÁO CÁO THÔNG SỐ RAM/CPU/DISK/DOCKER TRỰC TIẾP VÀO TOPIC 3
# Bot: vpsg24gbLinuxBot (Token: 8733078949:AAEQ-dSAU4OFrsMVAMOeQ9z_HgA2Ef-xHUM)
# Group: 4329103449 | Topic ID: 3 (vpsg24gb)
# ==============================================================================

BOT_TOKEN="8733078949:AAEQ-dSAU4OFrsMVAMOeQ9z_HgA2Ef-xHUM"
CHAT_ID="-1004329103449"
THREAD_ID=3

# 1. Lấy thông số hệ thống
HOSTNAME=$(hostname)
UPTIME=$(uptime -p | sed 's/up //')
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | xargs)

# RAM
RAM_TOTAL=$(free -h | awk '/Mem:/ {print $2}')
RAM_USED=$(free -h | awk '/Mem:/ {print $3}')
RAM_FREE=$(free -h | awk '/Mem:/ {print $4}')
RAM_PCT=$(free | awk '/Mem:/ {printf "%.1f", $3/$2 * 100}')

# SWAP
SWAP_TOTAL=$(free -h | awk '/Swap:/ {print $2}')
SWAP_USED=$(free -h | awk '/Swap:/ {print $3}')

# DISK
DISK_TOTAL=$(df -h / | awk 'NR==2 {print $2}')
DISK_USED=$(df -h / | awk 'NR==2 {print $3}')
DISK_PCT=$(df -h / | awk 'NR==2 {print $5}')

# CPU USAGE
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')

# DOCKER CONTAINERS
DOCKER_RUNNING=$(docker ps --format "{{.Names}}" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
if [ -z "$DOCKER_RUNNING" ]; then
    DOCKER_RUNNING="Không có container nào đang chạy"
fi

# 2. Định dạng tin nhắn HTML đẹp mắt
MESSAGE="📊 <b>BÁO CÁO THÔNG SỐ MÁY LOCAL [vpsg24gb]</b>

⏱️ Uptime: <code>${UPTIME}</code>
🔥 CPU Usage: <b>${CPU_USAGE}%</b> (Load: <code>${LOAD_AVG}</code>)
🧠 RAM: <b>${RAM_USED} / ${RAM_TOTAL}</b> (Đang dùng: <b>${RAM_PCT}%</b> | Trống: <code>${RAM_FREE}</code>)
💾 SWAP: <code>${SWAP_USED} / ${SWAP_TOTAL}</code>
💿 Disk /: <b>${DISK_USED} / ${DISK_TOTAL}</b> (Đã dùng: <b>${DISK_PCT}</b>)

🐳 <b>Docker Containers đang chạy:</b>
<code>${DOCKER_RUNNING}</code>

⚡ <i>Báo cáo trực tiếp từ hệ thống vpsg24gb.</i>"

# 3. Gửi tin nhắn Telegram vào Topic 3
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
     -H "Content-Type: application/json" \
     -d json_payload=$(jq -n \
        --arg chat_id "$CHAT_ID" \
        --arg thread_id "$THREAD_ID" \
        --arg text "$MESSAGE" \
        '{chat_id: $chat_id, message_thread_id: ($thread_id|tonumber), text: $text, parse_mode: "HTML"}')

echo "✅ Đã gửi báo cáo RAM/CPU/Disk vpsg24gb vào Topic 3 thành công!"
