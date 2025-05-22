#!/bin/bash
# 脚本模板 - 带参数，JSON输出
# 此脚本演示如何处理标准化参数结构并以JSON格式返回结果

# 输出JSON格式错误
output_error() {
  echo "{\"error\": \"$1\"}"
  exit 1
}

# 检查参数文件
if [ $# -lt 1 ]; then
  output_error "参数文件不存在"
fi

PARAMS_FILE=$1
if [ ! -f "$PARAMS_FILE" ]; then
  output_error "参数文件不存在: $PARAMS_FILE"
fi

# 检查是否有jq工具（用于解析JSON）
if ! command -v jq &> /dev/null; then
  output_error "缺少jq工具，无法解析JSON参数"
fi

# 从标准化参数结构中提取参数
# 用户参数
NAME=$(jq -r '.user_params.name // "World"' "$PARAMS_FILE")
VALUE=$(jq -r '.user_params.value // 42' "$PARAMS_FILE")

# 系统参数
EXECUTION_TIME=$(jq -r '.system_params.__execution_time // ""' "$PARAMS_FILE")

# 检查是否有上一个脚本的输出
if jq -e '.system_params.__prev_output' "$PARAMS_FILE" > /dev/null 2>&1; then
  HAS_PREV=true
  # 提取上一个脚本的输出（如果是对象，则尝试提取message字段）
  if jq -e '.system_params.__prev_output.message' "$PARAMS_FILE" > /dev/null 2>&1; then
    PREV_RESULT=$(jq -r '.system_params.__prev_output.message' "$PARAMS_FILE")
  else
    PREV_RESULT=$(jq -r '.system_params.__prev_output' "$PARAMS_FILE")
  fi
else
  HAS_PREV=false
  PREV_RESULT=""
fi

# 文件参数（如果有）
if jq -e '.file_params' "$PARAMS_FILE" > /dev/null 2>&1; then
  # 例如，获取输入文件路径
  INPUT_FILE=$(jq -r '.file_params.input_file // ""' "$PARAMS_FILE")
  OUTPUT_FILE=$(jq -r '.file_params.output_file // ""' "$PARAMS_FILE")
fi

# 处理业务逻辑
RESULT_VALUE=$((VALUE * 2))
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# 根据是否有前序输出，构建不同的JSON结果
if [ "$HAS_PREV" = true ]; then
  # 处理前一个脚本的输出
  RESULT="{
  \"message\": \"Hello, $NAME!\",
  \"value\": $RESULT_VALUE,
  \"processed_at\": \"$TIMESTAMP\",
  \"status\": \"success\",
  \"prev_output_processed\": true,
  \"prev_result\": \"$PREV_RESULT\"
}"
else
  RESULT="{
  \"message\": \"Hello, $NAME!\",
  \"value\": $RESULT_VALUE,
  \"processed_at\": \"$TIMESTAMP\",
  \"status\": \"success\"
}"
fi

# 输出结果
echo "$RESULT"
exit 0
