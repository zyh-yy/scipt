#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库插入脚本 - 无参数
直接向数据库中插入预定义的测试数据，无需额外参数输入
输出格式：纯文本
"""
import os
import sys
import sqlite3
import datetime
import json
import random

def is_in_docker():
    """检查是否在Docker容器中运行"""
    return os.path.exists('/.dockerenv')

def main():
    """主函数"""
    try:
        # 输出脚本开始执行信息
        print("数据库插入脚本（无参数）开始执行")
        print(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"在Docker中运行: {'是' if is_in_docker() else '否'}")
        print("--------------------------------------")
        
        # 数据库路径
        # Docker中的路径与主机可能不同，使用相对路径
        db_path = os.path.abspath("../database/scripts.db")
        if not os.path.exists(db_path):
            # 尝试其他可能的位置
            db_path = os.path.abspath("./database/scripts.db")
            if not os.path.exists(db_path):
                # 最后尝试直接使用相对于当前目录的路径
                db_path = "database/scripts.db"
        
        print(f"尝试连接数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 准备测试数据
        test_data = [
            {
                "name": f"测试脚本 {random.randint(1000, 9999)}",
                "description": "由db_insert_no_params.py自动生成的测试脚本数据",
                "file_path": f"scripts/auto_test_{random.randint(1000, 9999)}.py",
                "file_type": "python"
            },
            {
                "name": f"测试Shell {random.randint(1000, 9999)}",
                "description": "由db_insert_no_params.py自动生成的测试Shell数据",
                "file_path": f"scripts/auto_test_{random.randint(1000, 9999)}.sh",
                "file_type": "shell"
            },
            {
                "name": f"测试JS {random.randint(1000, 9999)}",
                "description": "由db_insert_no_params.py自动生成的测试JS数据",
                "file_path": f"scripts/auto_test_{random.randint(1000, 9999)}.js",
                "file_type": "javascript"
            }
        ]
        
        # 插入测试数据
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted_ids = []
        
        for data in test_data:
            cursor.execute('''
            INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (data["name"], data["description"], data["file_path"], data["file_type"], now, now))
            
            script_id = cursor.lastrowid
            inserted_ids.append(script_id)
            
            print(f"插入测试脚本数据: ID={script_id}, 名称={data['name']}")
        
        # 提交事务
        conn.commit()
        
        # 查询确认插入成功
        for script_id in inserted_ids:
            cursor.execute("SELECT id, name, file_type FROM scripts WHERE id = ?", (script_id,))
            result = cursor.fetchone()
            print(f"验证记录: ID={result[0]}, 名称={result[1]}, 类型={result[2]}")
        
        # 关闭数据库连接
        conn.close()
        
        print("--------------------------------------")
        print(f"数据库插入成功: 共插入 {len(inserted_ids)} 条记录")
        print(f"插入的记录ID: {', '.join(map(str, inserted_ids))}")
        print(f"执行完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0
    except sqlite3.Error as e:
        print(f"数据库错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"脚本执行出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
