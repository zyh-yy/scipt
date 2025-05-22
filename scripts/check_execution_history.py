#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查执行历史数据脚本
查询execution_history表中的数据
"""
import os
import sys
import sqlite3
import datetime
from tabulate import tabulate

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

def check_table_structure():
    """检查表结构"""
    print("\n检查execution_history表结构...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(execution_history)")
        columns = cursor.fetchall()
        
        # 打印表结构
        headers = ["序号", "字段名", "类型", "非空", "默认值", "主键"]
        rows = []
        for col in columns:
            rows.append([col['cid'], col['name'], col['type'], col['notnull'], col['dflt_value'], col['pk']])
        
        print(tabulate(rows, headers, tablefmt="grid"))
        
        # 检查是否有关键字段
        required_fields = ['id', 'script_id', 'chain_id', 'status', 'start_time', 'end_time', 'execution_time']
        missing_fields = [field for field in required_fields if field not in [col['name'] for col in columns]]
        
        if missing_fields:
            print(f"\n警告: 缺少关键字段: {', '.join(missing_fields)}")
        else:
            print("\n表结构检查通过: 所有关键字段都存在")
            
        conn.close()
    except Exception as e:
        print(f"检查表结构失败: {str(e)}")

def count_records():
    """统计记录数"""
    print("\n统计execution_history表记录数...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) as count FROM execution_history")
        result = cursor.fetchone()
        print(f"总记录数: {result['count']}")
        
        # 按status统计
        cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM execution_history 
        GROUP BY status
        """)
        status_counts = cursor.fetchall()
        
        if status_counts:
            print("\n按状态统计:")
            for status in status_counts:
                print(f"  {status['status']}: {status['count']}条")
        
        # 按执行类型统计
        cursor.execute("""
        SELECT 
            CASE 
                WHEN script_id IS NOT NULL THEN '脚本' 
                WHEN chain_id IS NOT NULL THEN '脚本链' 
                ELSE '未知' 
            END as type,
            COUNT(*) as count 
        FROM execution_history 
        GROUP BY type
        """)
        type_counts = cursor.fetchall()
        
        if type_counts:
            print("\n按执行类型统计:")
            for type_count in type_counts:
                print(f"  {type_count['type']}: {type_count['count']}条")
        
        # 检查有多少条记录有execution_time
        cursor.execute("SELECT COUNT(*) as count FROM execution_history WHERE execution_time IS NOT NULL")
        result = cursor.fetchone()
        print(f"\n有执行时间的记录数: {result['count']}")
        
        conn.close()
    except Exception as e:
        print(f"统计记录数失败: {str(e)}")

def sample_data(limit=5):
    """显示示例数据"""
    print(f"\n显示最近{limit}条execution_history记录:")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 获取最近的记录
        cursor.execute(f"""
        SELECT 
            id, script_id, chain_id, status, start_time, end_time, execution_time,
            substr(params, 1, 30) as params_preview,
            substr(output, 1, 30) as output_preview,
            substr(error, 1, 30) as error_preview
        FROM execution_history 
        ORDER BY id DESC 
        LIMIT {limit}
        """)
        records = cursor.fetchall()
        
        if records:
            # 转换为列表
            headers = ["ID", "脚本ID", "链ID", "状态", "开始时间", "结束时间", "执行时间(秒)", "参数预览", "输出预览", "错误预览"]
            rows = []
            for record in records:
                row = []
                for key in ['id', 'script_id', 'chain_id', 'status', 'start_time', 'end_time', 'execution_time', 'params_preview', 'output_preview', 'error_preview']:
                    value = record[key]
                    if value is not None and key.endswith('_preview') and len(str(value)) == 30:
                        value = f"{value}..."
                    row.append(value)
                rows.append(row)
            
            print(tabulate(rows, headers, tablefmt="grid"))
        else:
            print("没有找到记录")
            
        conn.close()
    except Exception as e:
        print(f"获取示例数据失败: {str(e)}")

def test_statistics_query():
    """测试统计查询"""
    print("\n测试统计查询...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 模拟get_statistics方法中的查询
        period = 'day'
        group_by = "strftime('%Y-%m-%d', start_time)"
        
        query = f'''
        SELECT 
            {group_by} as time_period,
            COUNT(*) as total_count,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
            AVG(execution_time) as avg_execution_time
        FROM execution_history
        GROUP BY {group_by}
        ORDER BY time_period ASC
        '''
        
        print(f"执行查询: {query}")
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"\n查询返回 {len(results)} 条记录")
        
        if results:
            # 转换为列表
            headers = ["日期", "总数", "成功", "失败", "平均执行时间(秒)"]
            rows = []
            for result in results:
                rows.append([
                    result['time_period'],
                    result['total_count'],
                    result['success_count'],
                    result['failed_count'],
                    result['avg_execution_time']
                ])
            
            print(tabulate(rows, headers, tablefmt="grid"))
        else:
            print("没有统计数据")
            
        conn.close()
    except Exception as e:
        print(f"测试统计查询失败: {str(e)}")

def add_sample_data(count=5):
    """添加示例数据"""
    print(f"\n添加{count}条示例执行历史记录...")
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
        
        if not script_id and not chain_id:
            print("没有找到脚本或脚本链，无法添加示例数据")
            return
        
        # 添加示例数据
        added_count = 0
        for i in range(count):
            # 交替添加脚本和脚本链的执行记录
            use_script = (i % 2 == 0 and script_id is not None)
            current_script_id = script_id if use_script else None
            current_chain_id = chain_id if not use_script and chain_id is not None else None
            
            # 如果两者都没有，使用脚本ID
            if current_script_id is None and current_chain_id is None:
                current_script_id = script_id
            
            # 设置状态，80%成功，20%失败
            status = "completed" if i % 5 != 4 else "failed"
            
            # 设置时间，分布在过去10天
            days_ago = i % 10
            start_time = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            end_time = (datetime.datetime.now() - datetime.timedelta(days=days_ago, minutes=(-30))).strftime('%Y-%m-%d %H:%M:%S')
            
            # 计算执行时间（秒）
            start_dt = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            execution_time = (end_dt - start_dt).total_seconds()
            
            # 添加记录
            cursor.execute('''
            INSERT INTO execution_history
            (script_id, chain_id, status, start_time, end_time, execution_time, params, output, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_script_id, 
                current_chain_id, 
                status, 
                start_time, 
                end_time, 
                execution_time,
                '{"sample": true}',
                '执行成功' if status == 'completed' else None,
                '执行失败示例错误' if status == 'failed' else None
            ))
            added_count += 1
        
        conn.commit()
        print(f"成功添加{added_count}条示例执行历史记录")
        conn.close()
    except Exception as e:
        print(f"添加示例数据失败: {str(e)}")

if __name__ == "__main__":
    print("开始检查执行历史数据...")
    
    # 检查表结构
    check_table_structure()
    
    # 统计记录数
    count_records()
    
    # 显示示例数据
    sample_data()
    
    # 测试统计查询
    test_statistics_query()
    
    # 如果没有足够的数据，添加一些示例数据
    if input("\n是否添加示例数据?(y/n) ").lower() == 'y':
        count = int(input("添加多少条示例数据? "))
        add_sample_data(count)
        
        # 再次统计和显示
        count_records()
        sample_data()
        test_statistics_query()
    
    print("\n检查完成")
