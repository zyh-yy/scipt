#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动添加示例执行历史数据
向execution_history表中添加示例数据，以便统计视图能够显示内容
无需交互式确认，直接运行
"""
import os
import sys
import sqlite3
import datetime
import json
import random

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目配置
from backend.config import DATABASE_PATH, logger

def get_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"获取数据库连接失败: {str(e)}")
        return None

def add_sample_data(days=30, records_per_day=3):
    """添加示例数据
    
    Args:
        days: 生成多少天的数据
        records_per_day: 每天生成多少条记录
    """
    print(f"正在添加{days}天的示例数据，每天{records_per_day}条...")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取一个脚本ID和一个脚本链ID
        cursor.execute("SELECT id FROM scripts LIMIT 1")
        script_result = cursor.fetchone()
        script_id = script_result['id'] if script_result else None
        
        cursor.execute("SELECT id FROM script_chains LIMIT 1")
        chain_result = cursor.fetchone()
        chain_id = chain_result['id'] if chain_result else None
        
        # 如果没有脚本或脚本链，创建一个示例脚本
        if not script_id and not chain_id:
            print("没有找到脚本或脚本链，创建示例脚本...")
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
            INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ('示例脚本', '用于测试的示例脚本', 'scripts/example.py', 'python', now, now))
            script_id = cursor.lastrowid
            conn.commit()
            print(f"创建了示例脚本，ID: {script_id}")
        
        # 添加示例数据
        added_count = 0
        total_records = days * records_per_day
        
        print(f"开始添加{total_records}条示例执行记录...")
        
        # 生成过去n天的数据
        for day in range(days):
            for record in range(records_per_day):
                # 交替添加脚本和脚本链的执行记录
                use_script = (record % 2 == 0 or chain_id is None)
                current_script_id = script_id if use_script else None
                current_chain_id = chain_id if not use_script and chain_id is not None else None
                
                # 设置状态，70%成功，20%失败，10%运行中
                status_rand = random.random()
                if status_rand < 0.7:
                    status = "completed"
                elif status_rand < 0.9:
                    status = "failed"
                else:
                    status = "running"
                
                # 设置时间
                hours_offset = random.randint(0, 23)
                minutes_offset = random.randint(0, 59)
                
                base_date = datetime.datetime.now() - datetime.timedelta(days=day)
                start_time = base_date.replace(hour=hours_offset, minute=minutes_offset)
                
                # 如果状态是已完成或失败，设置结束时间
                end_time = None
                execution_time = None
                if status in ["completed", "failed"]:
                    # 执行时间为1-600秒
                    exec_secs = random.randint(1, 600)
                    end_time = start_time + datetime.timedelta(seconds=exec_secs)
                    execution_time = exec_secs
                
                # 格式化时间
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None
                
                # 创建参数
                params = {
                    "sample": True,
                    "timestamp": start_time_str,
                    "random_value": random.randint(1, 1000)
                }
                
                # 添加记录
                cursor.execute('''
                INSERT INTO execution_history
                (script_id, chain_id, status, start_time, end_time, execution_time, params, output, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    current_script_id, 
                    current_chain_id, 
                    status, 
                    start_time_str, 
                    end_time_str, 
                    execution_time,
                    json.dumps(params),
                    f'示例输出 - 成功执行' if status == 'completed' else None,
                    f'示例错误 - 执行失败' if status == 'failed' else None
                ))
                added_count += 1
                
                # 每50条提交一次
                if added_count % 50 == 0:
                    conn.commit()
                    print(f"已添加 {added_count}/{total_records} 条记录...")
        
        # 最终提交
        conn.commit()
        print(f"成功添加 {added_count} 条示例执行历史记录")
        
        # 显示一些统计信息
        cursor.execute("SELECT COUNT(*) FROM execution_history")
        total = cursor.fetchone()[0]
        print(f"数据库中总共有 {total} 条执行历史记录")
        
        cursor.execute("SELECT COUNT(*) FROM execution_history WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM execution_history WHERE status = 'failed'")
        failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM execution_history WHERE status = 'running'")
        running = cursor.fetchone()[0]
        
        print(f"状态统计: 已完成 {completed}, 失败 {failed}, 运行中 {running}")
        
        conn.close()
        return added_count
    except Exception as e:
        print(f"添加示例数据失败: {str(e)}")
        return 0

if __name__ == "__main__":
    days = 30
    records_per_day = 3
    
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except:
            pass
    
    if len(sys.argv) > 2:
        try:
            records_per_day = int(sys.argv[2])
        except:
            pass
    
    # 直接添加示例数据，无需确认
    print(f"自动添加{days}天的示例数据，每天{records_per_day}条记录...")
    add_sample_data(days, records_per_day)
    print("示例数据添加完成")
