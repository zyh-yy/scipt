#!/bin/bash

# 获取系统信息
hostname=$(hostname)
os_name=$(uname -s)
kernel_version=$(uname -r)
current_time=$(date +"%Y-%m-%d %H:%M:%S")
uptime_info=$(uptime -p 2>/dev/null || echo "数据不可用")
total_memory=$(free -m | awk '/Mem:/ {print $2}')
used_memory=$(free -m | awk '/Mem:/ {print $3}')
free_memory=$(free -m | awk '/Mem:/ {print $4}')
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

# 构建JSON输出
cat << EOF
{
  "system_info": {
    "hostname": "$hostname",
    "os_name": "$os_name",
    "kernel_version": "$kernel_version",
    "current_time": "$current_time",
    "uptime": "$uptime_info"
  },
  "performance": {
    "memory": {
      "total_mb": $total_memory,
      "used_mb": $used_memory,
      "free_mb": $free_memory
    },
    "cpu_usage_percent": $cpu_usage,
    "disk_usage_percent": $disk_usage
  }
}
EOF
