#!/bin/bash
# 脚本版本内容修复工具
# 该脚本扫描所有脚本版本，读取文件内容并更新到数据库中

# 数据库路径
DB_PATH="database/scripts.db"

# 检查数据库是否存在
if [ ! -f "$DB_PATH" ]; then
    echo "{\"error\": \"数据库文件不存在: $DB_PATH\"}"
    exit 1
fi

# 检查数据库中是否有content列
HAS_CONTENT_COLUMN=$(sqlite3 "$DB_PATH" "PRAGMA table_info(script_versions);" | grep -c "content")

# 如果没有content列，添加它
if [ "$HAS_CONTENT_COLUMN" -eq "0" ]; then
    echo "添加content列到script_versions表..."
    sqlite3 "$DB_PATH" "ALTER TABLE script_versions ADD COLUMN content TEXT;"
fi

# 获取所有版本记录
VERSION_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM script_versions;")
echo "{\"total_versions\": $VERSION_COUNT, \"processed\": 0, \"updated\": 0, \"failed\": 0, \"details\": ["

# 处理计数器
PROCESSED=0
UPDATED=0
FAILED=0

# 获取所有版本ID和文件路径
while IFS="|" read -r version_id script_id file_path; do
    PROCESSED=$((PROCESSED+1))
    
    # 跳过已有内容的记录
    HAS_CONTENT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM script_versions WHERE id=$version_id AND content IS NOT NULL AND content != '';")
    
    if [ "$HAS_CONTENT" -eq "1" ]; then
        # 已有内容，跳过
        continue
    fi
    
    # 检查文件是否存在
    if [ -f "$file_path" ]; then
        # 读取文件内容
        CONTENT=$(cat "$file_path")
        
        # 转义内容中的引号
        ESCAPED_CONTENT=$(echo "$CONTENT" | sed 's/"/\\"/g')
        
        # 更新数据库
        sqlite3 "$DB_PATH" "UPDATE script_versions SET content=\"$ESCAPED_CONTENT\" WHERE id=$version_id;"
        
        if [ $? -eq 0 ]; then
            UPDATED=$((UPDATED+1))
            echo "{\"version_id\": $version_id, \"script_id\": $script_id, \"status\": \"updated\"},"
        else
            FAILED=$((FAILED+1))
            echo "{\"version_id\": $version_id, \"script_id\": $script_id, \"status\": \"failed\", \"reason\": \"数据库更新失败\"},"
        fi
    else
        # 文件不存在，尝试从脚本原始文件读取
        ORIGINAL_FILE_PATH=$(sqlite3 "$DB_PATH" "SELECT file_path FROM scripts WHERE id=$script_id;")
        
        if [ -f "$ORIGINAL_FILE_PATH" ]; then
            # 读取原始文件内容
            CONTENT=$(cat "$ORIGINAL_FILE_PATH")
            
            # 转义内容中的引号
            ESCAPED_CONTENT=$(echo "$CONTENT" | sed 's/"/\\"/g')
            
            # 更新数据库
            sqlite3 "$DB_PATH" "UPDATE script_versions SET content=\"$ESCAPED_CONTENT\" WHERE id=$version_id;"
            
            if [ $? -eq 0 ]; then
                UPDATED=$((UPDATED+1))
                echo "{\"version_id\": $version_id, \"script_id\": $script_id, \"status\": \"updated_from_original\"},"
            else
                FAILED=$((FAILED+1))
                echo "{\"version_id\": $version_id, \"script_id\": $script_id, \"status\": \"failed\", \"reason\": \"数据库更新失败\"},"
            fi
        else
            FAILED=$((FAILED+1))
            echo "{\"version_id\": $version_id, \"script_id\": $script_id, \"status\": \"failed\", \"reason\": \"文件不存在\"},"
        fi
    fi
done < <(sqlite3 "$DB_PATH" "SELECT id, script_id, file_path FROM script_versions ORDER BY script_id, id;")

# 输出结果
echo "{\"summary\": {\"processed\": $PROCESSED, \"updated\": $UPDATED, \"failed\": $FAILED}}]}"
