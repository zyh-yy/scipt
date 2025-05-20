#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库结构修复脚本
为execution_history表添加缺失的execution_time字段
"""
import os
import sys
import sqlite3
from pathlib import Path

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.config import logger, DATABASE_PATH

def fix_database_structure():
    """修复数据库表结构"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        print("修复前检查数据库表结构:")
        # 检查execution_history表结构
        cursor.execute("PRAGMA table_info(execution_history)")
        columns = cursor.fetchall()
        print("\nexecution_history表结构:")
        for col in columns:
            print(f"  {col}")
        
        # 检查是否缺少execution_time字段
        has_execution_time = any(col[1] == 'execution_time' for col in columns)
        
        if not has_execution_time:
            print("\n需要添加execution_time字段...")
            # 添加execution_time字段
            cursor.execute('''
            ALTER TABLE execution_history
            ADD COLUMN execution_time REAL
            ''')
            conn.commit()
            print("成功添加execution_time字段")
            
            # 更新已有记录的execution_time
            print("正在为已有记录计算execution_time...")
            cursor.execute('''
            UPDATE execution_history
            SET execution_time = (
                JULIANDAY(end_time) - JULIANDAY(start_time)
            ) * 86400
            WHERE start_time IS NOT NULL AND end_time IS NOT NULL
            ''')
            conn.commit()
            rows_updated = cursor.rowcount
            print(f"成功更新{rows_updated}条记录的execution_time")
        else:
            print("\nexecution_time字段已存在，无需修复")
        
        # 验证修复后的表结构
        print("\n修复后检查数据库表结构:")
        cursor.execute("PRAGMA table_info(execution_history)")
        columns = cursor.fetchall()
        print("execution_history表结构:")
        for col in columns:
            print(f"  {col}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"修复数据库结构失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始修复数据库结构...")
    if fix_database_structure():
        print("数据库结构修复完成")
    else:
        print("数据库结构修复失败")
