#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复执行历史记录的日期分布
将现有执行历史记录的日期分散到过去30天中
"""
import os
import sys
import sqlite3
import random
from datetime import datetime, timedelta

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def fix_execution_dates(script_id=None, days=30):
    """
    修复执行历史记录的日期分布
    
    Args:
        script_id: 指定脚本ID，None表示所有脚本
        days: 将记录分散到过去多少天
    """
    try:
        # 连接数据库
        conn = sqlite3.connect(os.path.join(project_root, 'database/scripts.db'))
        cursor = conn.cursor()
        
        # 查询需要修复的记录
        if script_id:
            print(f"开始修复脚本ID {script_id} 的执行历史记录日期...")
            cursor.execute("SELECT id FROM execution_history WHERE script_id = ?", (script_id,))
        else:
            print("开始修复所有执行历史记录日期...")
            cursor.execute("SELECT id FROM execution_history")
        
        record_ids = [row[0] for row in cursor.fetchall()]
        total_records = len(record_ids)
        print(f"找到 {total_records} 条记录需要修复")
        
        if total_records == 0:
            print("没有找到需要修复的记录")
            conn.close()
            return False
        
        # 获取当前日期
        now = datetime.now()
        
        # 准备过去days天的日期列表
        dates = []
        for day in range(days):
            date = now - timedelta(days=day)
            dates.append(date)
        
        # 随机分配记录到不同日期
        print("正在分配记录到过去30天的日期...")
        updated_count = 0
        
        for record_id in record_ids:
            # 随机选择一个日期
            date = random.choice(dates)
            
            # 随机选择一个时间点
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            # 组合成完整的日期时间
            datetime_str = date.strftime(f'%Y-%m-%d {hour:02d}:{minute:02d}:{second:02d}')
            
            # 更新记录
            cursor.execute(
                "UPDATE execution_history SET start_time = ? WHERE id = ?",
                (datetime_str, record_id)
            )
            
            updated_count += 1
            if updated_count % 50 == 0:
                print(f"已更新 {updated_count}/{total_records} 条记录")
        
        # 提交事务
        conn.commit()
        conn.close()
        
        print(f"成功将 {updated_count} 条记录分散到过去 {days} 天")
        return True
    except Exception as e:
        print(f"修复执行历史记录日期失败: {str(e)}")
        return False

if __name__ == "__main__":
    # 获取脚本ID
    if len(sys.argv) > 1:
        script_id = int(sys.argv[1])
        fix_execution_dates(script_id)
    else:
        fix_execution_dates()
