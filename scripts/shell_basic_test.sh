#!/bin/bash
# Shell基础测试脚本
# 用于测试Shell脚本的执行能力和系统信息获取

# 检查参数文件是否存在
if [ $# -lt 1 ]; then
    echo '{"error": "缺少参数文件"}'
    exit 1
fi

PARAMS_FILE=$1

if [ ! -f "$PARAMS_FILE" ]; then
    echo '{"error": "参数文件不存在: '"$PARAMS_FILE"'"}'
    exit 1
fi

# 收集系统信息
OS_INFO=$(uname -a)
HOST_NAME=$(hostname)
CURRENT_DIR=$(pwd)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# 检查是否在Docker中运行
if [ -f "/.dockerenv" ]; then
    DOCKER_STATUS="可能在Docker中运行"
else
    DOCKER_STATUS="未在Docker中运行"
fi

# 获取CPU信息
if [ -f "/proc/cpuinfo" ]; then
    CPU_INFO=$(cat /proc/cpuinfo | grep "model name" | head -n 1 | sed 's/model name\s*: //')
else
    CPU_INFO="无法获取CPU信息"
fi

# 获取内存信息
if [ -f "/proc/meminfo" ]; then
    MEM_TOTAL=$(cat /proc/meminfo | grep "MemTotal" | awk '{print $2}')
    MEM_FREE=$(cat /proc/meminfo | grep "MemFree" | awk '{print $2}')
else
    MEM_TOTAL="无法获取"
    MEM_FREE="无法获取"
fi

# 获取目录内容
DIR_CONTENT=$(ls -la | head -10)

# 读取传入的参数
PARAM_CONTENT=$(cat $PARAMS_FILE)

# 输出JSON格式结果
cat << EOF
{
  "script_type": "Shell基础测试",
  "execution_time": "$TIMESTAMP",
  "system_info": {
    "os_info": "$OS_INFO",
    "hostname": "$HOST_NAME",
    "cpu_info": "$CPU_INFO",
    "memory_total_kb": "$MEM_TOTAL",
    "memory_free_kb": "$MEM_FREE",
    "docker": "$DOCKER_STATUS"
  },
  "current_directory": "$CURRENT_DIR",
  "directory_sample": "$(echo "$DIR_CONTENT" | tr '\n' ' ' | sed 's/"/\\"/g')",
  "params_file_content": $PARAM_CONTENT,
  "message": "Shell基础测试脚本执行成功"
}
EOF

exit 0
