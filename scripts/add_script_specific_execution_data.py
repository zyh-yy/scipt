#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为特定脚本ID添加执行历史数据
"""
import os
import sys
import json
import random
import datetime
from datetime import timedelta

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.models.execution import ExecutionHistory

def add_script_execution_data(script_id, days=30, records_per_day=3):
    """
    为特定脚本ID添加执行历史数据
    
    Args:
        script_id: 脚本ID
        days: 添加多少天的数据
        records_per_day: 每天添加多少条记录
    """
    print(f"将为脚本ID {script_id} 添加 {days} 天的执行数据，每天 {records_per_day} 条记录...")
    
    # 确认是否继续
    confirm = input("确认添加特定脚本的执行数据? (y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    # 获取当前日期
    now = datetime.datetime.now()
    
    # 记录添加的数量
    added_count = 0
    
    print(f"开始添加 {days * records_per_day} 条执行记录...")
    
    # 为每一天添加多条记录
    for day in range(days):
        # 计算日期
        date = now - timedelta(days=day)
        
        # 每天添加多条记录
        for i in range(records_per_day):
            # 记录间隔几小时
            hour_offset = random.randint(0, 23)
            minute_offset = random.randint(0, 59)
            
            # 设置开始时间
            start_time = date.replace(hour=hour_offset, minute=minute_offset)
            
            # 随机状态
            status_options = ["completed", "failed", "running"]
            weights = [0.7, 0.2, 0.1]  # 70% 完成, 20% 失败, 10% 运行中
            status = random.choices(status_options, weights=weights)[0]
            
            # 如果状态是已完成或失败，设置结束时间
            end_time = None
            if status in ["completed", "failed"]:
                # 随机执行时间，从几秒到几分钟
                execution_seconds = random.randint(1, 600)
                end_time = start_time + timedelta(seconds=execution_seconds)
            
            # 创建参数
            params = {
                "param1": f"value{random.randint(1, 100)}",
                "param2": random.randint(1, 1000)
            }
            
            # 创建输出
            output = None
            error = None
            
            if status == "completed":
                output = f"脚本执行成功，生成了 {random.randint(1, 100)} 条数据。"
            elif status == "failed":
                error = f"脚本执行失败: 错误代码 {random.randint(1, 10)}"
            
            # 添加到数据库
            history_id = ExecutionHistory.add(
                script_id=script_id,
                status=status,
                params=params,
                output=output,
                error=error
            )
            
            # 如果状态是已完成或失败，更新结束时间
            if status in ["completed", "failed"] and history_id:
                # 计算执行时间（秒）
                execution_time = (end_time - start_time).total_seconds()
                
                # 格式化时间为字符串
                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 连接数据库并更新
                import sqlite3
                conn = sqlite3.connect(os.path.join(project_root, 'database/scripts.db'))
                cursor = conn.cursor()
                
                cursor.execute('''
                UPDATE execution_history
                SET end_time = ?, execution_time = ?
                WHERE id = ?
                ''', (end_time_str, execution_time, history_id))
                
                conn.commit()
                conn.close()
            
            if history_id:
                added_count += 1
            
            # 显示进度
            if added_count % 15 == 0:
                print(f"已添加 {added_count}/{days * records_per_day} 条记录...")
    
    # 获取总数
    import sqlite3
    conn = sqlite3.connect(os.path.join(project_root, 'database/scripts.db'))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM execution_history WHERE script_id = ?", (script_id,))
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM execution_history")
    all_count = cursor.fetchone()[0]
    
    # 统计状态
    cursor.execute('''
    SELECT status, COUNT(*) FROM execution_history 
    WHERE script_id = ?
    GROUP BY status
    ''', (script_id,))
    status_counts = cursor.fetchall()
    
    conn.close()
    
    # 显示结果
    print(f"成功添加 {added_count} 条执行历史记录")
    print(f"脚本ID {script_id} 总共有 {total_count} 条执行历史记录")
    print(f"数据库中总共有 {all_count} 条执行历史记录")
    
    status_info = ", ".join([f"{status} {count}" for status, count in status_counts])
    print(f"脚本ID {script_id} 的状态统计: {status_info}")
    
    print("示例数据添加完成")

if __name__ == "__main__":
    # 获取脚本ID
    if len(sys.argv) > 1:
        script_id = int(sys.argv[1])
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        records_per_day = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    else:
        script_id = int(input("请输入要添加执行数据的脚本ID: "))
        days = int(input("请输入要添加的天数 (默认 30): ") or "30")
        records_per_day = int(input("请输入每天添加的记录数 (默认 3): ") or "3")
    
    add_script_execution_data(script_id, days, records_per_day)
