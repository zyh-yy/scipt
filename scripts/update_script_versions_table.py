# -*- coding: utf-8 -*-
"""
更新script_versions表，添加版本控制所需的新字段
"""
import os
import sys
import sqlite3
from datetime import datetime

# 添加项目根目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import logger

def update_script_versions_table():
    """更新script_versions表，添加新字段"""
    try:
        # 连接数据库
        conn = sqlite3.connect('database/scripts.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='script_versions'")
        if not cursor.fetchone():
            logger.error("script_versions表不存在")
            return False
        
        # 检查description字段是否存在
        cursor.execute("PRAGMA table_info(script_versions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 添加description字段
        if 'description' not in columns:
            logger.info("添加description字段")
            cursor.execute("ALTER TABLE script_versions ADD COLUMN description TEXT")
        
        # 添加created_at字段
        if 'created_at' not in columns:
            logger.info("添加created_at字段")
            cursor.execute("ALTER TABLE script_versions ADD COLUMN created_at DATETIME")
            
            # 为现有记录设置创建时间
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE script_versions SET created_at = ? WHERE created_at IS NULL", (now,))
        
        # 添加content_hash字段
        if 'content_hash' not in columns:
            logger.info("添加content_hash字段")
            cursor.execute("ALTER TABLE script_versions ADD COLUMN content_hash TEXT")
            
            # 更新现有记录的content_hash
            cursor.execute("SELECT id, file_path FROM script_versions")
            versions = cursor.fetchall()
            
            import hashlib
            for version_id, file_path in versions:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            content_hash = hashlib.sha256(f.read()).hexdigest()
                        cursor.execute("UPDATE script_versions SET content_hash = ? WHERE id = ?", 
                                      (content_hash, version_id))
                    except Exception as e:
                        logger.error(f"计算文件哈希值失败: {file_path}, {str(e)}")
        
        conn.commit()
        conn.close()
        
        logger.info("script_versions表更新成功")
        return True
    except Exception as e:
        logger.error(f"更新script_versions表失败: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    result = update_script_versions_table()
    print("更新结果:", "成功" if result else "失败")
