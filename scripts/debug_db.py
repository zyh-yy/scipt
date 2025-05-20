#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库调试脚本
检查数据库表结构并尝试插入数据
"""
import os
import sys
import json
import sqlite3
from pathlib import Path

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.config import logger, DATABASE_PATH
from backend.models.base import initialize_db

def check_database_structure():
    """检查数据库表结构"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库包含以下表: {[t[0] for t in tables]}")
        
        # 检查scripts表结构
        cursor.execute("PRAGMA table_info(scripts)")
        columns = cursor.fetchall()
        print("\nscripts表结构:")
        for col in columns:
            print(f"  {col}")
        
        # 尝试插入一条测试记录
        try:
            test_name = "测试脚本"
            test_desc = "用于测试的脚本"
            test_path = "/test/path.py"
            test_type = "py"
            
            # 构建动态插入语句
            columns = [col[1] for col in columns if col[1] not in ('id', 'created_at', 'updated_at')]
            placeholders = ['?'] * len(columns)
            values = []
            
            # 为每个列准备值
            for col in columns:
                if col == 'name':
                    values.append(test_name)
                elif col == 'description':
                    values.append(test_desc)
                elif col == 'file_path':
                    values.append(test_path)
                elif col == 'file_type':
                    values.append(test_type)
                elif col == 'url_path':
                    values.append(None)
                elif col == 'is_deleted':
                    values.append(0)
                else:
                    values.append(None)
            
            # 打印将要执行的SQL
            sql = f"INSERT INTO scripts ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            print(f"\n将要执行的SQL: {sql}")
            print(f"值: {values}")
            
            # 执行插入
            cursor.execute(sql, values)
            conn.commit()
            print(f"测试记录插入成功, ID: {cursor.lastrowid}")
            
            # 删除测试记录
            cursor.execute("DELETE FROM scripts WHERE name=?", (test_name,))
            conn.commit()
            print("测试记录已删除")
            
        except Exception as e:
            print(f"插入测试记录失败: {str(e)}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"检查数据库结构失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始诊断数据库...")
    print("初始化数据库...")
    initialize_db()
    print("数据库初始化完成")
    if check_database_structure():
        print("数据库诊断完成")
    else:
        print("数据库诊断失败")
