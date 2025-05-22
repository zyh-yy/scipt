#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将创建的脚本插入到系统数据库中
"""
import os
import sys
import sqlite3
import datetime
import json

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

def main():
    """主函数"""
    try:
        print("开始将脚本插入到数据库...")
        
        # 要插入的脚本列表
        scripts_to_insert = [
            "scripts/db_insert_no_params.py",
            "scripts/db_insert_with_params_json.py",
            "scripts/db_insert_shell_table.sh",
            "scripts/db_insert_js_xml.js",
            "scripts/db_export_csv.py"
        ]
        
        # 查找数据库
        db_path = find_database()
        if not db_path:
            print("错误: 无法找到数据库文件")
            return 1
        
        print(f"使用数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 当前时间
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted_ids = []
        
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
            inserted_ids.append(script_id)
            
            print(f"插入脚本: ID={script_id}, 名称={script_name}, 类型={script_type}, 输出模式={output_mode}")
            
            # 如果脚本接受参数，添加参数记录
            if has_parameters:
                # 添加一个示例参数
                param_name = "example_param"
                param_desc = "示例参数"
                param_type = "string"
                is_required = 0
                default_value = ""
                
                if "json" in script_path.lower():
                    param_name = "json_param"
                    param_desc = "JSON参数示例"
                    default_value = '{"key": "value"}'
                elif "csv" in script_path.lower():
                    param_name = "csv_param"
                    param_desc = "CSV参数示例"
                    default_value = "data.csv"
                elif "xml" in script_path.lower():
                    param_name = "xml_param"
                    param_desc = "XML参数示例"
                    default_value = "<root><item>value</item></root>"
                
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
                
                print(f"  添加参数: {param_name}, 类型={param_type}")
        
        # 提交事务
        conn.commit()
        
        # 创建脚本版本记录
        for script_id in inserted_ids:
            cursor.execute("SELECT id, name, file_path FROM scripts WHERE id = ?", (script_id,))
            script = cursor.fetchone()
            
            if script:
                script_id, script_name, script_path = script
                
                # 读取脚本内容
                content = read_script_content(script_path)
                if content is None:
                    continue
                
                # 插入版本记录
                cursor.execute('''
                INSERT INTO script_versions
                (script_id, version, content, created_at, created_by)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    script_id,
                    "1.0.0",
                    content,
                    now,
                    "system"
                ))
                
                print(f"创建脚本版本: 脚本ID={script_id}, 版本=1.0.0")
        
        # 提交事务
        conn.commit()
        
        # 关闭数据库连接
        conn.close()
        
        print(f"成功插入 {len(inserted_ids)} 个脚本到数据库")
        return 0
    
    except sqlite3.Error as e:
        print(f"数据库错误: {str(e)}")
        return 1
    except Exception as e:
        print(f"脚本执行出错: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
