#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面的脚本数据插入工具 - 向所有脚本相关表格插入测试数据
"""
import os
import sys
import sqlite3
import datetime
import json
import random
import hashlib

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

def read_script_content(file_path):
    """读取脚本内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {str(e)}")
        return None

def get_script_description(content):
    """从脚本内容中提取描述"""
    if not content:
        return "无描述"
    
    lines = content.split('\n')
    for line in lines[:20]:  # 只检查前20行
        line = line.strip()
        if line.startswith('"""') or line.startswith("'''"):
            # 提取多行注释
            start_idx = lines.index(line)
            if line.endswith('"""') or line.endswith("'''"):
                return line.strip('"""').strip("'''").strip()
            
            for end_idx in range(start_idx + 1, min(start_idx + 10, len(lines))):
                if '"""' in lines[end_idx] or "'''" in lines[end_idx]:
                    return '\n'.join(lines[start_idx+1:end_idx]).strip()
            
        elif line.startswith('#'):
            # 提取单行注释
            return line.lstrip('#').strip()
    
    return "数据库操作脚本"

def get_output_mode(content, file_path):
    """根据脚本内容和文件名确定输出模式"""
    if not content:
        return "text"
    
    lower_content = content.lower()
    
    if "json.dumps" in lower_content or "json格式" in lower_content:
        return "json"
    elif "csv" in lower_content or "csv格式" in lower_content:
        return "csv"
    elif "xml" in lower_content or "xml格式" in lower_content:
        return "xml"
    elif "print_table" in lower_content or "表格" in lower_content:
        return "table"
    
    # 根据文件名判断
    if "json" in file_path.lower():
        return "json"
    elif "csv" in file_path.lower():
        return "csv"
    elif "xml" in file_path.lower():
        return "xml"
    elif "table" in file_path.lower():
        return "table"
    
    return "text"

def get_script_type(file_path):
    """根据文件扩展名确定脚本类型"""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.py':
        return "python"
    elif ext == '.js':
        return "javascript"
    elif ext == '.sh':
        return "shell"
    elif ext == '.bat':
        return "batch"
    elif ext == '.ps1':
        return "powershell"
    
    return "unknown"

def has_params(content, file_path):
    """判断脚本是否接受参数"""
    if not content:
        return False
    
    lower_content = content.lower()
    
    # 检查是否有处理参数的代码
    if "sys.argv" in lower_content or "process.argv" in lower_content or "$1" in lower_content:
        return True
    
    # 根据文件名判断
    if "with_params" in file_path.lower() or "params" in file_path.lower():
        return True
    
    return False

def generate_md5(content):
    """生成内容的MD5哈希值"""
    if not content:
        return ""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def main():
    """主函数"""
    try:
        print("开始全面插入脚本相关数据...")
        
        # 要插入的脚本列表
        intended_scripts = [
            "scripts/db_insert_no_params.py",
            "scripts/db_insert_with_params_json.py",
            "scripts/db_insert_shell_table.sh",
            "scripts/db_insert_js_xml.js",
            "scripts/db_export_csv.py"
        ]
        
        # 检查脚本是否存在
        scripts_to_insert = []
        missing_scripts = []
        for script_path in intended_scripts:
            if os.path.exists(script_path):
                scripts_to_insert.append(script_path)
            else:
                missing_scripts.append(script_path)
        
        if missing_scripts:
            print("警告: 以下脚本文件不存在:")
            for script in missing_scripts:
                print(f"  - {script}")
        
        if not scripts_to_insert:
            print("错误: 没有可用的脚本文件可以插入数据库")
            return 1
        
        print(f"将插入以下脚本 ({len(scripts_to_insert)}):")
        for script in scripts_to_insert:
            print(f"  - {script}")
        
        # 查找数据库
        db_path = find_database()
        if not db_path:
            print("错误: 无法找到数据库文件")
            return 1
        
        print(f"使用数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询数据库中的表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"数据库中的表格: {', '.join(tables)}")
        
        # 当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted_script_ids = []
        
        # 第1步: 插入脚本基本信息
        print("\n--- 步骤1: 插入脚本基本信息 ---")
        for script_path in scripts_to_insert:
            if not os.path.exists(script_path):
                print(f"警告: 脚本文件不存在: {script_path}")
                continue
            
            # 读取脚本内容
            content = read_script_content(script_path)
            if content is None:
                continue
            
            # 获取脚本信息
            script_name = os.path.basename(script_path)
            script_type = get_script_type(script_path)
            description = get_script_description(content)
            output_mode = get_output_mode(content, script_path)
            has_parameters = has_params(content, script_path)
            
            # 插入脚本记录
            cursor.execute('''
            INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at, output_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                script_name,
                description,
                script_path,
                script_type,
                now,
                now,
                output_mode
            ))
            
            script_id = cursor.lastrowid
            inserted_script_ids.append(script_id)
            
            print(f"插入脚本: ID={script_id}, 名称={script_name}, 类型={script_type}, 输出模式={output_mode}")
        
        conn.commit()
        
        # 第2步: 插入脚本参数
        print("\n--- 步骤2: 插入脚本参数 ---")
        for script_id in inserted_script_ids:
            # 查询脚本信息
            cursor.execute("SELECT id, name, file_path FROM scripts WHERE id = ?", (script_id,))
            script = cursor.fetchone()
            
            if not script:
                continue
                
            script_id, script_name, script_path = script
            
            # 判断是否需要添加参数
            has_parameters = has_params(read_script_content(script_path), script_path)
            
            if has_parameters:
                # 添加两个参数
                param_types = ["string", "number", "select", "file", "boolean"]
                
                for i in range(2):
                    param_name = f"param_{i+1}"
                    param_desc = f"参数 #{i+1} 描述"
                    param_type = random.choice(param_types)
                    is_required = i % 2  # 偶数索引为非必填参数
                    
                    # 根据参数类型设置默认值
                    if param_type == "string":
                        default_value = f"默认值_{i}"
                    elif param_type == "number":
                        default_value = str(i * 10)
                    elif param_type == "select":
                        default_value = f"选项_{i}"
                    elif param_type == "file":
                        default_value = f"file_{i}.txt"
                    elif param_type == "boolean":
                        default_value = "true" if i % 2 else "false"
                    else:
                        default_value = ""
                    
                    cursor.execute('''
                    INSERT INTO script_parameters
                    (script_id, name, description, param_type, is_required, default_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        script_id,
                        param_name,
                        param_desc,
                        param_type,
                        is_required,
                        default_value
                    ))
                    
                    param_id = cursor.lastrowid
                    print(f"  添加参数: 脚本ID={script_id}, 参数ID={param_id}, 名称={param_name}, 类型={param_type}")
        
        conn.commit()
        
        # 第3步: 插入脚本版本
        print("\n--- 步骤3: 插入脚本版本 ---")
        if "script_versions" in tables:
            # 查询表结构
            cursor.execute("PRAGMA table_info(script_versions)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"脚本版本表列: {', '.join(columns)}")
            
            for script_id in inserted_script_ids:
                # 查询脚本信息
                cursor.execute("SELECT id, name, file_path FROM scripts WHERE id = ?", (script_id,))
                script = cursor.fetchone()
                
                if not script:
                    continue
                    
                script_id, script_name, script_path = script
                
                # 读取脚本内容
                content = read_script_content(script_path)
                if content is None:
                    continue
                
                # 生成内容哈希
                content_hash = generate_md5(content)
                
                # 插入版本记录
                try:
                    # 准备基本字段
                    fields = ["script_id", "version"]
                    values = [script_id, "1.0.0"]
                    
                    # 添加其他存在的字段
                    if "file_path" in columns:
                        fields.append("file_path")
                        values.append(script_path)
                        
                    if "is_current" in columns:
                        fields.append("is_current")
                        values.append(1)
                        
                    if "created_at" in columns:
                        fields.append("created_at")
                        values.append(now)
                        
                    if "description" in columns:
                        fields.append("description")
                        values.append(f"初始版本 - {now}")
                        
                    if "content_hash" in columns:
                        fields.append("content_hash")
                        values.append(content_hash)
                        
                    if "content" in columns:
                        fields.append("content")
                        values.append(content)
                    
                    # 构建SQL
                    placeholders = ", ".join(["?" for _ in fields])
                    sql = f"INSERT INTO script_versions ({', '.join(fields)}) VALUES ({placeholders})"
                    
                    cursor.execute(sql, values)
                    version_id = cursor.lastrowid
                    
                    print(f"  添加版本: 脚本ID={script_id}, 版本ID={version_id}, 版本=1.0.0")
                except sqlite3.Error as e:
                    print(f"  警告: 为脚本ID {script_id} 添加版本失败: {str(e)}")
        else:
            print("  脚本版本表不存在，跳过此步骤")
        
        conn.commit()
        
        # 第4步: 插入执行历史
        print("\n--- 步骤4: 插入执行历史 ---")
        if "execution_history" in tables:
            for script_id in inserted_script_ids:
                # 为每个脚本添加2条执行记录
                for i in range(2):
                    # 计算随机的执行时间
                    start_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 10), hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    duration = random.randint(1, 300)  # 1-300秒
                    end_time = start_time + datetime.timedelta(seconds=duration)
                    
                    # 随机状态
                    status = random.choice(["success", "failed", "running"])
                    
                    # 生成输出
                    if status == "success":
                        output = f"脚本执行成功，处理了 {random.randint(1, 100)} 条记录。"
                        error = None
                    elif status == "failed":
                        output = "脚本开始执行..."
                        error = f"执行失败: {random.choice(['数据库连接错误', '参数无效', '权限不足', '超时'])}"
                    else:  # running
                        output = "脚本正在执行中..."
                        error = None
                    
                    # 插入执行记录
                    try:
                        cursor.execute('''
                        INSERT INTO execution_history
                        (script_id, chain_id, status, start_time, end_time, duration, output, error)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            script_id,
                            None,
                            status,
                            start_time.strftime('%Y-%m-%d %H:%M:%S'),
                            end_time.strftime('%Y-%m-%d %H:%M:%S') if status != "running" else None,
                            duration if status != "running" else None,
                            output,
                            error
                        ))
                        
                        history_id = cursor.lastrowid
                        print(f"  添加执行历史: 脚本ID={script_id}, 历史ID={history_id}, 状态={status}")
                    except sqlite3.Error as e:
                        print(f"  警告: 为脚本ID {script_id} 添加执行历史失败: {str(e)}")
        else:
            print("  执行历史表不存在，跳过此步骤")
        
        conn.commit()
        
        # 第5步: 创建脚本链
        print("\n--- 步骤5: 创建脚本链 ---")
        if "script_chains" in tables and len(inserted_script_ids) >= 3:
            # 创建一个包含3个脚本的链
            chain_name = f"测试脚本链 {datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            chain_description = "包含多个数据库操作脚本的测试链"
            
            cursor.execute('''
            INSERT INTO script_chains (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (chain_name, chain_description, now, now))
            
            chain_id = cursor.lastrowid
            
            # 添加链中的节点
            for i, script_id in enumerate(inserted_script_ids[:3]):
                try:
                    cursor.execute('''
                    INSERT INTO chain_nodes (chain_id, script_id, node_order, created_at)
                    VALUES (?, ?, ?, ?)
                    ''', (chain_id, script_id, i + 1, now))
                    
                    node_id = cursor.lastrowid
                    print(f"  添加链节点: 链ID={chain_id}, 节点ID={node_id}, 脚本ID={script_id}, 顺序={i+1}")
                except sqlite3.Error as e:
                    print(f"  警告: 为链ID {chain_id} 添加节点失败: {str(e)}")
            
            # 添加链的执行历史
            if "execution_history" in tables:
                # 计算随机的执行时间
                start_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 5), hours=random.randint(0, 12))
                duration = random.randint(10, 600)  # 10-600秒
                end_time = start_time + datetime.timedelta(seconds=duration)
                
                # 随机状态
                status = random.choice(["success", "failed"])
                
                # 生成输出
                if status == "success":
                    output = f"脚本链执行成功，执行了 {len(inserted_script_ids[:3])} 个脚本。"
                    error = None
                else:  # failed
                    output = f"执行了 {random.randint(1, len(inserted_script_ids[:3]))} 个脚本后失败。"
                    error = f"执行失败: {random.choice(['数据库连接错误', '脚本间数据传递失败', '权限不足', '超时'])}"
                
                try:
                    cursor.execute('''
                    INSERT INTO execution_history
                    (script_id, chain_id, status, start_time, end_time, duration, output, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        None,
                        chain_id,
                        status,
                        start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        duration,
                        output,
                        error
                    ))
                    
                    history_id = cursor.lastrowid
                    print(f"  添加链执行历史: 链ID={chain_id}, 历史ID={history_id}, 状态={status}")
                except sqlite3.Error as e:
                    print(f"  警告: 为链ID {chain_id} 添加执行历史失败: {str(e)}")
        else:
            print("  脚本链表不存在或脚本数量不足，跳过此步骤")
        
        conn.commit()
        
        # 第6步: 创建调度任务
        print("\n--- 步骤6: 创建调度任务 ---")
        if "scheduled_tasks" in tables and inserted_script_ids:
            # 为第一个脚本创建定时任务
            script_id = inserted_script_ids[0]
            
            # 查询脚本信息
            cursor.execute("SELECT name FROM scripts WHERE id = ?", (script_id,))
            script_name = cursor.fetchone()[0]
            
            task_name = f"{script_name} 定时任务"
            cron_expression = "0 0 * * *"  # 每天午夜
            
            # 是否已激活
            is_active = 1
            
            try:
                cursor.execute('''
                INSERT INTO scheduled_tasks
                (script_id, chain_id, name, cron_expression, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    script_id,
                    None,
                    task_name,
                    cron_expression,
                    is_active,
                    now,
                    now
                ))
                
                task_id = cursor.lastrowid
                print(f"  添加调度任务: 任务ID={task_id}, 名称={task_name}, Cron={cron_expression}")
            except sqlite3.Error as e:
                print(f"  警告: 创建调度任务失败: {str(e)}")
        else:
            print("  调度任务表不存在，跳过此步骤")
        
        conn.commit()
        
        # 关闭数据库连接
        conn.close()
        
        print("\n全面插入完成!")
        print(f"共插入 {len(inserted_script_ids)} 个脚本及相关数据")
        return 0
    
    except sqlite3.Error as e:
        print(f"数据库错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"脚本执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
