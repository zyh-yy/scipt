#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查定时任务表状态
"""
import os
import sys
import sqlite3
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from backend.config import DATABASE_PATH

def main():
    try:
        # 连接数据库
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scheduled_tasks'")
        if not cursor.fetchone():
            print("定时任务表不存在！")
            return
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(scheduled_tasks)")
        columns = cursor.fetchall()
        print("定时任务表结构:")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        print()
        
        # 获取表中的数据
        cursor.execute("SELECT * FROM scheduled_tasks")
        tasks = cursor.fetchall()
        if not tasks:
            print("定时任务表为空，没有定时任务记录")
        else:
            print(f"共有 {len(tasks)} 条定时任务记录:")
            for task in tasks:
                task_dict = dict(task)
                # 转换参数为可读形式
                if task_dict.get('params'):
                    try:
                        params = json.loads(task_dict['params'])
                        task_dict['params'] = params
                    except:
                        pass
                
                print(json.dumps(task_dict, indent=2, ensure_ascii=False))
                print("-" * 50)
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
