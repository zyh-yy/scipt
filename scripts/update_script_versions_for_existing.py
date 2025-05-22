#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为现有脚本更新版本记录
检查所有脚本，为没有版本记录的脚本创建初始版本
"""
import os
import sys
import sqlite3
import datetime

# 获取当前脚本的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
# 将根目录添加到模块搜索路径
sys.path.append(ROOT_DIR)

from backend.models.script.script_version import ScriptVersion
from backend.models.script.script_base import Script

def find_database():
    """查找数据库文件"""
    possible_paths = [
        os.path.join(ROOT_DIR, "database", "scripts.db"),
        os.path.join(SCRIPT_DIR, "..", "database", "scripts.db"),
        "database/scripts.db",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def get_scripts_without_versions(conn):
    """获取没有版本记录的脚本"""
    cursor = conn.cursor()
    
    # 查询所有未删除的脚本
    cursor.execute("""
    SELECT s.id, s.name, s.file_path 
    FROM scripts s
    WHERE s.is_deleted = 0
    """)
    
    all_scripts = cursor.fetchall()
    
    scripts_without_versions = []
    
    for script in all_scripts:
        script_id = script[0]
        
        # 检查是否有版本记录
        cursor.execute("""
        SELECT COUNT(*) 
        FROM script_versions 
        WHERE script_id = ?
        """, (script_id,))
        
        version_count = cursor.fetchone()[0]
        
        if version_count == 0:
            scripts_without_versions.append(script)
    
    return scripts_without_versions

def main():
    """主函数"""
    print("开始为现有脚本创建版本记录...")
    
    # 查找数据库
    db_path = find_database()
    if not db_path:
        print("错误: 无法找到数据库文件")
        return 1
    
    print(f"使用数据库: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # 获取没有版本记录的脚本
        scripts = get_scripts_without_versions(conn)
        
        if not scripts:
            print("所有脚本都已有版本记录，无需创建")
            return 0
        
        print(f"找到 {len(scripts)} 个没有版本记录的脚本")
        
        # 为每个脚本创建版本记录
        for script in scripts:
            script_id = script[0]
            script_name = script[1]
            file_path = script[2]
            
            print(f"为脚本 ID={script_id} 名称='{script_name}' 创建版本记录...")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"  警告: 文件不存在: {file_path}")
                continue
            
            # 创建版本记录
            version_id = ScriptVersion.add(script_id, file_path, version="1.0.0", description="初始版本")
            
            if version_id:
                print(f"  成功创建版本记录: ID={version_id}")
            else:
                print(f"  创建版本记录失败")
        
        print(f"版本记录创建完成")
        return 0
    
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1
    
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
