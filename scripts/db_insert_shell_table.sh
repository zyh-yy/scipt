#!/bin/bash
# 数据库插入脚本 - Shell版本，表格输出
# 接受参数并向数据库中插入数据，以表格形式输出结果

# 检查是否在Docker中运行
check_docker() {
    if [ -f "/.dockerenv" ]; then
        echo "是"
    else
        echo "否"
    fi
}

# 查找数据库文件
find_database() {
    for db_path in "../database/scripts.db" "./database/scripts.db" "database/scripts.db" "/app/database/scripts.db"; do
        if [ -f "$db_path" ]; then
            echo "$db_path"
            return 0
        fi
    done
    echo ""
    return 1
}

# 格式化表格输出
print_table_header() {
    printf "+--------+--------------------------------+--------------------------------+--------------------------------+\n"
    printf "| %-6s | %-30s | %-30s | %-30s |\n" "ID" "名称" "路径" "类型"
    printf "+--------+--------------------------------+--------------------------------+--------------------------------+\n"
}

print_table_row() {
    printf "| %-6s | %-30s | %-30s | %-30s |\n" "$1" "$2" "$3" "$4"
}

print_table_footer() {
    printf "+--------+--------------------------------+--------------------------------+--------------------------------+\n"
}

# 检查参数文件是否存在
if [ $# -lt 1 ]; then
    echo "错误: 缺少参数文件"
    exit 1
fi

PARAMS_FILE=$1

if [ ! -f "$PARAMS_FILE" ]; then
    echo "错误: 参数文件不存在: $PARAMS_FILE"
    exit 1
fi

# 输出脚本信息
echo "数据库插入脚本 (Shell版本) - 表格输出格式"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "在Docker中运行: $(check_docker)"
echo ""

# 查找数据库
DB_PATH=$(find_database)

if [ -z "$DB_PATH" ]; then
    echo "错误: 无法找到数据库文件"
    exit 1
fi

echo "使用数据库: $DB_PATH"
echo ""

# 检查是否安装了SQLite3
if ! command -v sqlite3 &> /dev/null; then
    echo "错误: 未安装sqlite3命令行工具"
    
    # 尝试安装SQLite3（适用于Ubuntu/Debian）
    if command -v apt-get &> /dev/null; then
        echo "尝试安装sqlite3..."
        apt-get update && apt-get install -y sqlite3
        
        if ! command -v sqlite3 &> /dev/null; then
            echo "安装sqlite3失败"
            exit 1
        fi
        
        echo "sqlite3安装成功"
    else
        echo "无法自动安装sqlite3，请手动安装后重试"
        exit 1
    fi
fi

# 从参数文件中读取数据
# 这里假设参数文件是JSON格式
TABLE_NAME=$(cat $PARAMS_FILE | grep -o '"table_name"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/"table_name"[[:space:]]*:[[:space:]]*"\([^"]*\)"/\1/')
TABLE_NAME=${TABLE_NAME:-"scripts"}  # 默认使用scripts表

# 生成随机ID作为脚本名称后缀
RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)

# 准备当前时间
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 插入数据
echo "正在向 $TABLE_NAME 表插入数据..."

# 插入Shell脚本记录
SCRIPT_NAME="Shell脚本 $RANDOM_ID"
FILE_PATH="scripts/shell_test_$RANDOM_ID.sh"
DESCRIPTION="由db_insert_shell_table.sh生成的测试数据"
FILE_TYPE="shell"

# 执行SQL插入
SCRIPT_ID=$(sqlite3 "$DB_PATH" "INSERT INTO $TABLE_NAME (name, description, file_path, file_type, created_at, updated_at) VALUES ('$SCRIPT_NAME', '$DESCRIPTION', '$FILE_PATH', '$FILE_TYPE', '$CURRENT_TIME', '$CURRENT_TIME'); SELECT last_insert_rowid();")

if [ -z "$SCRIPT_ID" ]; then
    echo "错误: 插入数据失败"
    exit 1
fi

# 插入Python脚本记录
SCRIPT_NAME2="Shell生成的Python脚本 $RANDOM_ID"
FILE_PATH2="scripts/shell_gen_py_$RANDOM_ID.py"
DESCRIPTION2="由Shell脚本生成的Python测试数据"
FILE_TYPE2="python"

# 执行SQL插入
SCRIPT_ID2=$(sqlite3 "$DB_PATH" "INSERT INTO $TABLE_NAME (name, description, file_path, file_type, created_at, updated_at) VALUES ('$SCRIPT_NAME2', '$DESCRIPTION2', '$FILE_PATH2', '$FILE_TYPE2', '$CURRENT_TIME', '$CURRENT_TIME'); SELECT last_insert_rowid();")

if [ -z "$SCRIPT_ID2" ]; then
    echo "错误: 插入第二条数据失败"
    exit 1
fi

# 查询插入的记录
echo ""
echo "成功插入以下记录:"
print_table_header

# 查询并显示第一条记录
RESULT=$(sqlite3 "$DB_PATH" "SELECT id, name, file_path, file_type FROM $TABLE_NAME WHERE id = $SCRIPT_ID")
ID=$(echo $RESULT | cut -d'|' -f1)
NAME=$(echo $RESULT | cut -d'|' -f2)
PATH=$(echo $RESULT | cut -d'|' -f3)
TYPE=$(echo $RESULT | cut -d'|' -f4)
print_table_row "$ID" "$NAME" "$PATH" "$TYPE"

# 查询并显示第二条记录
RESULT2=$(sqlite3 "$DB_PATH" "SELECT id, name, file_path, file_type FROM $TABLE_NAME WHERE id = $SCRIPT_ID2")
ID2=$(echo $RESULT2 | cut -d'|' -f1)
NAME2=$(echo $RESULT2 | cut -d'|' -f2)
PATH2=$(echo $RESULT2 | cut -d'|' -f3)
TYPE2=$(echo $RESULT2 | cut -d'|' -f4)
print_table_row "$ID2" "$NAME2" "$PATH2" "$TYPE2"

print_table_footer

# 输出统计信息
echo ""
echo "总计: 成功插入 2 条记录"
echo "执行完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 如果参数中指定了需要添加参数，则为脚本添加参数
if grep -q '"add_parameters"[[:space:]]*:[[:space:]]*true' "$PARAMS_FILE"; then
    echo "正在为脚本添加参数..."
    
    # 为第一个脚本添加参数
    PARAM_NAME="shell_param"
    PARAM_DESC="Shell脚本参数"
    PARAM_TYPE="string"
    IS_REQUIRED=1
    DEFAULT_VALUE="default_value"
    
    sqlite3 "$DB_PATH" "INSERT INTO script_parameters (script_id, name, description, param_type, is_required, default_value) VALUES ($SCRIPT_ID, '$PARAM_NAME', '$PARAM_DESC', '$PARAM_TYPE', $IS_REQUIRED, '$DEFAULT_VALUE')"
    
    # 为第二个脚本添加参数
    PARAM_NAME2="py_param"
    PARAM_DESC2="Python脚本参数"
    PARAM_TYPE2="number"
    IS_REQUIRED2=0
    DEFAULT_VALUE2="42"
    
    sqlite3 "$DB_PATH" "INSERT INTO script_parameters (script_id, name, description, param_type, is_required, default_value) VALUES ($SCRIPT_ID2, '$PARAM_NAME2', '$PARAM_DESC2', '$PARAM_TYPE2', $IS_REQUIRED2, '$DEFAULT_VALUE2')"
    
    echo "参数添加完成"
fi

exit 0
