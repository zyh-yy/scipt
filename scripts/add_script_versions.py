#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为脚本添加版本信息

此脚本用于为chain_test_1_generate.py、chain_test_2_process.py、chain_test_3_report.py
三个脚本添加版本信息，解决前端无法看到脚本内容的问题。
"""

import os
import sys
import json
import datetime
import sqlite3

# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 导入数据库模型类
from backend.models.script.script_version import ScriptVersion
from backend.models import Script, DBManager
from config import DATABASE_PATH, logger

def main():
    """主函数"""
    print(json.dumps({
        "status": "开始",
        "message": "开始为脚本添加版本信息",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 确保script_versions表存在
    ensure_version_table_exists()
    
    # 检查脚本文件是否存在
    script_files = [
        "scripts/chain_test_1_generate.py",
        "scripts/chain_test_2_process.py",
        "scripts/chain_test_3_report.py"
    ]
    
    for script_file in script_files:
        if not os.path.exists(script_file):
            print(json.dumps({
                "status": "错误",
                "message": f"脚本文件 {script_file} 不存在",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return 1
    
    try:
        # 获取数据库中的脚本信息
        scripts = get_scripts_by_file_paths(script_files)
        
        if not scripts:
            print(json.dumps({
                "status": "错误",
                "message": "数据库中未找到相关脚本",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return 1
        
        # 添加版本信息
        success_count = 0
        for script in scripts:
            # 检查是否已有版本
            has_version = check_version_exists(script["id"])
            if has_version:
                print(json.dumps({
                    "status": "信息",
                    "message": f"脚本 ID {script['id']} ({script['name']}) 已有版本信息，跳过",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                success_count += 1
                continue
            
            # 添加版本信息
            version_id = add_script_version_directly(
                script["id"], 
                script["file_path"], 
                f"初始版本 - {script['name']}"
            )
            
            if version_id:
                print(json.dumps({
                    "status": "成功",
                    "message": f"为脚本 ID {script['id']} ({script['name']}) 添加版本信息成功",
                    "version_id": version_id,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                success_count += 1
            else:
                print(json.dumps({
                    "status": "错误",
                    "message": f"为脚本 ID {script['id']} ({script['name']}) 添加版本信息失败",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
        
        # 输出总结信息
        print(json.dumps({
            "status": "完成",
            "message": f"版本信息添加完成，成功 {success_count}/{len(scripts)} 个",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        
        return 0 if success_count == len(scripts) else 1
        
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "异常",
            "message": f"发生异常: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return 1

def ensure_version_table_exists():
    """确保script_versions表存在"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='script_versions'")
        if not cursor.fetchone():
            # 创建表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS script_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                script_id INTEGER NOT NULL,
                version TEXT NOT NULL,
                file_path TEXT NOT NULL,
                is_current INTEGER DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_hash TEXT,
                FOREIGN KEY (script_id) REFERENCES scripts (id)
            )
            ''')
            conn.commit()
            print(json.dumps({
                "status": "信息",
                "message": "script_versions表不存在，已创建",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        
        conn.close()
        return True
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"确保script_versions表存在失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return False

def get_scripts_by_file_paths(file_paths):
    """根据文件路径获取脚本信息"""
    try:
        conn = DBManager.get_connection()
        conn.row_factory = DBManager.dict_factory
        cursor = conn.cursor()
        
        # 构建查询条件
        placeholders = ", ".join(["?" for _ in file_paths])
        query = f"SELECT * FROM scripts WHERE file_path IN ({placeholders}) AND is_deleted = 0"
        
        cursor.execute(query, file_paths)
        scripts = cursor.fetchall()
        
        conn.close()
        return scripts
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"获取脚本信息失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return []

def check_version_exists(script_id):
    """检查脚本是否已有版本信息"""
    try:
        conn = DBManager.get_connection()
        conn.row_factory = DBManager.dict_factory
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM script_versions WHERE script_id = ?", (script_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result["count"] > 0
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"检查脚本版本失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return False

def add_script_version_directly(script_id, file_path, description):
    """直接添加脚本版本信息"""
    try:
        # 计算文件内容的哈希值
        content_hash = calculate_file_hash(file_path)
        if not content_hash:
            print(json.dumps({
                "status": "错误",
                "message": f"计算文件哈希值失败: {file_path}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return None
        
        conn = DBManager.get_connection()
        cursor = conn.cursor()
        
        # 使用初始版本号
        version = "1.0.0"
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加新版本
        cursor.execute('''
        INSERT INTO script_versions 
        (script_id, version, file_path, is_current, description, created_at, content_hash)
        VALUES (?, ?, ?, 1, ?, ?, ?)
        ''', (script_id, version, file_path, description, now, content_hash))
        
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return version_id
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"添加脚本版本失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return None

def calculate_file_hash(file_path):
    """计算文件内容的SHA-256哈希值"""
    import hashlib
    try:
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        return None

if __name__ == "__main__":
    sys.exit(main())
