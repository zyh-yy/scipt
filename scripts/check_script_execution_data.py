#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查脚本执行数据分组情况
"""
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def check_script_execution_data(script_id=None):
    """检查脚本执行数据分组情况"""
    try:
        # 连接数据库
        conn = sqlite3.connect(os.path.join(project_root, 'database/scripts.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询脚本执行记录总数
        if script_id:
            cursor.execute("SELECT COUNT(*) FROM execution_history WHERE script_id = ?", (script_id,))
            print(f"脚本ID {script_id} 执行历史记录总数: {cursor.fetchone()[0]}")
        else:
            cursor.execute("SELECT COUNT(*) FROM execution_history")
            print(f"执行历史记录总数: {cursor.fetchone()[0]}")
        
        # 检查是否有缺失start_time的记录
        if script_id:
            cursor.execute("SELECT COUNT(*) FROM execution_history WHERE script_id = ? AND start_time IS NULL", (script_id,))
        else:
            cursor.execute("SELECT COUNT(*) FROM execution_history WHERE start_time IS NULL")
        
        null_start_time_count = cursor.fetchone()[0]
        print(f"缺失start_time的记录数: {null_start_time_count}")
        
        # 查看日期分组统计
        print("\n按日期分组统计:")
        if script_id:
            cursor.execute("""
            SELECT strftime('%Y-%m-%d', start_time) as date, COUNT(*) as count
            FROM execution_history
            WHERE script_id = ? AND start_time IS NOT NULL
            GROUP BY date
            ORDER BY date
            """, (script_id,))
        else:
            cursor.execute("""
            SELECT strftime('%Y-%m-%d', start_time) as date, COUNT(*) as count
            FROM execution_history
            WHERE start_time IS NOT NULL
            GROUP BY date
            ORDER BY date
            """)
        
        date_counts = cursor.fetchall()
        for row in date_counts:
            print(f"  {row['date']}: {row['count']}条记录")
        
        print(f"\n按日期分组后共有{len(date_counts)}组数据")
        
        # 查看状态分布
        print("\n按状态统计:")
        if script_id:
            cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM execution_history
            WHERE script_id = ?
            GROUP BY status
            """, (script_id,))
        else:
            cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM execution_history
            GROUP BY status
            """)
        
        status_counts = cursor.fetchall()
        for row in status_counts:
            print(f"  {row['status']}: {row['count']}条记录")
        
        # 检查分组问题
        print("\n查看内部实现逻辑使用的分组SQL:")
        period = 'day'
        group_by = "strftime('%Y-%m-%d', start_time)"
        
        query = f"""
        SELECT 
            {group_by} as time_period,
            COUNT(*) as total_count,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(execution_time) as avg_execution_time
        FROM execution_history
        """
        
        params = []
        where_clauses = []
        
        if script_id:
            where_clauses.append("script_id = ?")
            params.append(script_id)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += f" GROUP BY {group_by} ORDER BY time_period ASC"
        
        print(f"SQL查询: {query}")
        print(f"查询参数: {params}")
        
        cursor.execute(query, params)
        stats = cursor.fetchall()
        
        print(f"查询返回 {len(stats)} 条统计数据")
        if len(stats) > 0:
            print("统计数据示例:")
            for i, stat in enumerate(stats[:3]):
                print(f"  第{i+1}条:")
                for key in stat.keys():
                    print(f"    {key}: {stat[key]}")
                print("")
        
        conn.close()
        return True
    except Exception as e:
        print(f"检查脚本执行数据分组情况失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 获取脚本ID
    if len(sys.argv) > 1:
        script_id = int(sys.argv[1])
        check_script_execution_data(script_id)
    else:
        check_script_execution_data()
