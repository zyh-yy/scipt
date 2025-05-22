#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库导出脚本 - 无参数，CSV输出
将数据库中的脚本信息导出为CSV格式
输出格式：CSV
"""
import os
import sys
import sqlite3
import datetime
import csv
import io

def is_in_docker():
    """检查是否在Docker容器中运行"""
    return os.path.exists('/.dockerenv')

def find_database():
    """查找数据库文件"""
    possible_paths = [
        os.path.abspath("../database/scripts.db"),
        os.path.abspath("./database/scripts.db"),
        "database/scripts.db",
        "/app/database/scripts.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def export_to_csv(rows, headers):
    """将记录导出为CSV格式"""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    
    # 写入头部
    writer.writerow(headers)
    
    # 写入数据行
    for row in rows:
        writer.writerow(row)
    
    return output.getvalue()

def main():
    """主函数"""
    try:
        print(f"数据库导出脚本 (CSV格式) - 开始执行")
        print(f"当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"在Docker中运行: {'是' if is_in_docker() else '否'}")
        print("-" * 50)
        
        # 查找数据库
        db_path = find_database()
        if not db_path:
            print(f"错误: 无法找到数据库文件")
            return 1
        
        print(f"使用数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 准备查询
        print(f"正在查询数据...")
        
        # 查询脚本表
        cursor.execute('''
        SELECT id, name, description, file_path, file_type, created_at, updated_at
        FROM scripts
        WHERE is_deleted = 0
        ORDER BY id DESC
        LIMIT 50
        ''')
        
        scripts = cursor.fetchall()
        print(f"查询到 {len(scripts)} 条脚本记录")
        
        # 导出脚本信息为CSV
        script_headers = ["ID", "名称", "描述", "文件路径", "类型", "创建时间", "更新时间"]
        scripts_csv = export_to_csv(scripts, script_headers)
        
        print("-" * 50)
        print("脚本数据 (CSV格式):")
        print(scripts_csv)
        print("-" * 50)
        
        # 查询脚本参数表
        cursor.execute('''
        SELECT sp.id, s.name as script_name, sp.name, sp.description, sp.param_type, sp.is_required, sp.default_value
        FROM script_parameters sp
        JOIN scripts s ON sp.script_id = s.id
        WHERE s.is_deleted = 0
        ORDER BY sp.id DESC
        LIMIT 50
        ''')
        
        params = cursor.fetchall()
        print(f"查询到 {len(params)} 条参数记录")
        
        # 导出参数信息为CSV
        params_headers = ["ID", "脚本名称", "参数名称", "描述", "参数类型", "是否必须", "默认值"]
        params_csv = export_to_csv(params, params_headers)
        
        print("参数数据 (CSV格式):")
        print(params_csv)
        print("-" * 50)
        
        # 查询执行历史表
        cursor.execute('''
        SELECT 
            h.id, 
            COALESCE(s.name, c.name, '直接执行') as source_name,
            h.status, 
            h.start_time, 
            h.end_time,
            CASE WHEN h.script_id IS NOT NULL THEN '脚本' WHEN h.chain_id IS NOT NULL THEN '脚本链' ELSE '未知' END as type
        FROM execution_history h
        LEFT JOIN scripts s ON h.script_id = s.id
        LEFT JOIN script_chains c ON h.chain_id = c.id
        ORDER BY h.id DESC
        LIMIT 50
        ''')
        
        history = cursor.fetchall()
        print(f"查询到 {len(history)} 条执行历史记录")
        
        # 导出执行历史为CSV
        history_headers = ["ID", "来源名称", "状态", "开始时间", "结束时间", "类型"]
        history_csv = export_to_csv(history, history_headers)
        
        print("执行历史数据 (CSV格式):")
        print(history_csv)
        print("-" * 50)
        
        # 计算统计数据并插入数据库
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算各种脚本类型的数量
        cursor.execute('''
        SELECT file_type, COUNT(*) 
        FROM scripts 
        WHERE is_deleted = 0 
        GROUP BY file_type
        ''')
        type_counts = cursor.fetchall()
        
        # 将统计结果作为新记录插入
        cursor.execute('''
        INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            f"统计报告 {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            f"由db_export_csv.py自动生成的统计报告，包含各类型脚本数量",
            f"reports/stats_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
            "report",
            now,
            now
        ))
        
        report_id = cursor.lastrowid
        
        # 为统计报告添加一些参数，用于保存统计数据
        for file_type, count in type_counts:
            cursor.execute('''
            INSERT INTO script_parameters
            (script_id, name, description, param_type, is_required, default_value)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                report_id,
                f"count_{file_type}",
                f"{file_type}类型脚本数量",
                "number",
                0,
                str(count)
            ))
        
        # 提交事务
        conn.commit()
        
        # 输出新创建的统计记录
        cursor.execute('''
        SELECT id, name, file_path FROM scripts WHERE id = ?
        ''', (report_id,))
        report = cursor.fetchone()
        
        print(f"已创建统计报告记录: ID={report[0]}, 名称={report[1]}, 路径={report[2]}")
        
        # 查询刚刚插入的统计参数
        cursor.execute('''
        SELECT name, param_type, default_value 
        FROM script_parameters 
        WHERE script_id = ?
        ''', (report_id,))
        stats_params = cursor.fetchall()
        
        print("统计数据:")
        for param in stats_params:
            print(f"  - {param[0]}: {param[2]} ({param[1]})")
        
        # 关闭数据库连接
        conn.close()
        
        print("-" * 50)
        print(f"数据导出完成")
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
