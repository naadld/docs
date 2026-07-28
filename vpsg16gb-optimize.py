#!/usr/bin/env python3
import json
import subprocess
import urllib.request
import sys
import html

BOT_TOKEN = "8027319967:AAERPtaSTFjxtPjaOx3dZ00__MoD_XVIQc8"
CHAT_ID = "-1004329103449"
THREAD_ID = 2

def clean_str(val) -> str:
    return html.escape(str(val).strip())

def run_cmd(cmd: str) -> str:
    return subprocess.getoutput(cmd).strip()

def analyze_system():
    # 1. Top Memory processes
    top_mem_raw = run_cmd("ps -eo comm,%mem,%cpu --sort=-%mem | head -n 6 | tail -n 5")
    top_mem_lines = []
    for line in top_mem_raw.split('\n'):
        parts = line.split()
        if len(parts) >= 3:
            name, mem, cpu = parts[0], parts[1], parts[2]
            top_mem_lines.append(f"• <code>{clean_str(name[:20])}</code>: RAM {mem}% | CPU {cpu}%")

    # 2. Top CPU processes
    top_cpu_raw = run_cmd("ps -eo comm,%cpu,%mem --sort=-%cpu | head -n 6 | tail -n 5")
    top_cpu_lines = []
    for line in top_cpu_raw.split('\n'):
        parts = line.split()
        if len(parts) >= 3:
            name, cpu, mem = parts[0], parts[1], parts[2]
            top_cpu_lines.append(f"• <code>{clean_str(name[:20])}</code>: CPU {cpu}% | RAM {mem}%")

    # 3. Docker stats
    docker_stats_raw = run_cmd("docker stats --no-stream --format '{{.Name}}: RAM {{.MemPerc}} ({{.MemUsage}})' 2>/dev/null | head -n 5")
    docker_lines = []
    if docker_stats_raw:
        for line in docker_stats_raw.split('\n'):
            docker_lines.append(f"• <code>{clean_str(line)}</code>")
    else:
        docker_lines.append("• <i>No active containers</i>")

    # 4. Memory & Disk health metrics
    ram_pct = float(run_cmd("free | awk '/Mem:/ {printf \"%.1f\", $3/$2 * 100}'") or 0)
    swap_pct = float(run_cmd("free | awk '/Swap:/ {if ($2>0) printf \"%.1f\", $3/$2 * 100; else print 0}'") or 0)
    disk_pct = float(run_cmd("df / | awk 'NR==2 {printf \"%.1f\", $3/$2 * 100}'") or 0)

    # 5. Generate Smart Recommendations
    recommendations = []
    if ram_pct > 80:
        recommendations.append("⚠️ <b>High Memory Usage</b>: Run <code>sync && echo 3 > /proc/sys/vm/drop_caches</code> to clear inactive RAM cache.")
    else:
        recommendations.append("✅ <b>RAM Health Good</b>: Memory usage is within normal operating threshold.")

    if swap_pct > 30:
        recommendations.append("⚠️ <b>Swap Pressure Detected</b>: Run <code>swapoff -a && swapon -a</code> to flush swap memory.")

    docker_disk = run_cmd("docker system df --format '{{.Type}}: {{.Size}}' 2>/dev/null | tr '\n' ' | '")
    if "GB" in docker_disk:
        recommendations.append("🧹 <b>Docker Cleanup Recommended</b>: Run <code>docker system prune -f</code> to reclaim unused disk space.")
    else:
        recommendations.append("✅ <b>Disk Storage Optimal</b>: System disk utilization is healthy.")

    report = f"""🔍 <b>SYSTEM OPTIMIZATION ANALYZER [vpsg16gb]</b>

🔥 <b>Top CPU Consuming Processes:</b>
{chr(10).join(top_cpu_lines)}

🧠 <b>Top Memory Consuming Processes:</b>
{chr(10).join(top_mem_lines)}

🐳 <b>Docker Container Resource Usage:</b>
{chr(10).join(docker_lines)}

💡 <b>OPTIMIZATION RECOMMENDATIONS:</b>
{chr(10).join(recommendations)}"""
    return report

def main():
    report_text = analyze_system()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "message_thread_id": THREAD_ID,
        "text": report_text,
        "parse_mode": "HTML"
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("✅ Successfully sent vpsg16gb optimization report to Topic 2!")
    except Exception as e:
        print(f"❌ Failed to send optimization report: {e}")

if __name__ == "__main__":
    main()
