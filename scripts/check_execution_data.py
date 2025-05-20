#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查执行历史数据脚本
查看execution_history表中的数据，特别是execution_time字段的值
"""
import os
import sys
import sqlite3
import json
from pathlib import Path

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.config import logger, DATABASE_PATH

def check_execution_data():
    """检查执行历史数据"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查记录总数
        cursor.execute("SELECT COUNT(*) as count FROM execution_history")
        count = cursor.fetchone()['count']
        print(f"execution_history表中共有{count}条记录")
        
        # 检查有多少记录的execution_time不为空
        cursor.execute("SELECT COUNT(*) as count FROM execution_history WHERE execution_time IS NOT NULL")
        valid_count = cursor.fetchone()['count']
        print(f"其中{valid_count}条记录的execution_time不为空")
        
        # 检查有多少记录的status为completed
        cursor.execute("SELECT COUNT(*) as count FROM execution_history WHERE status = 'completed'")
        completed_count = cursor.fetchone()['count']
        print(f"其中{completed_count}条记录的status为completed")
        
        # 检查有多少记录有start_time和end_time
        cursor.execute("""
        SELECT COUNT(*) as count FROM execution_history 
        WHERE start_time IS NOT NULL AND end_time IS NOT NULL
        """)
        time_count = cursor.fetchone()['count']
        print(f"其中{time_count}条记录同时有start_time和end_time")
        
        # 检查最近5条记录的详细信息
        print("\n最近5条执行历史记录:")
        cursor.execute("""
        SELECT id, script_id, chain_id, status, start_time, end_time, execution_time
        FROM execution_history
        ORDER BY id DESC
        LIMIT 5
        """)
        records = cursor.fetchall()
        for record in records:
            print(f"  ID: {record['id']}")
            print(f"  脚本ID: {record['script_id']}")
            print(f"  脚本链ID: {record['chain_id']}")
            print(f"  状态: {record['status']}")
            print(f"  开始时间: {record['start_time']}")
            print(f"  结束时间: {record['end_time']}")
            print(f"  执行时间: {record['execution_time']}")
            print(f"  ----------------------")
        
        # 尝试手动执行统计查询
        print("\n尝试执行统计查询:")
        try:
            cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d', start_time) as time_period,
                COUNT(*) as total_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                AVG(execution_time) as avg_execution_time
            FROM execution_history
            GROUP BY strftime('%Y-%m-%d', start_time)
            ORDER BY time_period ASC
            """)
            stats = cursor.fetchall()
            print(f"查询成功，共获取{len(stats)}条统计数据")
            
            if stats:
                print("\n统计数据示例:")
                for i, stat in enumerate(stats[:3]):
                    print(f"  第{i+1}条:")
                    print(f"    日期: {stat['time_period']}")
                    print(f"    总执行次数: {stat['total_count']}")
                    print(f"    成功次数: {stat['success_count']}")
                    print(f"    失败次数: {stat['failed_count']}")
                    print(f"    平均执行时间: {stat['avg_execution_time']}")
            
        except Exception as e:
            print(f"执行统计查询失败: {str(e)}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"检查执行历史数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始检查执行历史数据...")
    if check_execution_data():
        print("执行历史数据检查完成")
    else:
        print("执行历史数据检查失败")
