#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库插入脚本 - 有参数，JSON输出
根据传入参数向数据库中插入数据，并以JSON格式返回结果
"""
import os
import sys
import json
import sqlite3
import datetime
import uuid

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

def main():
    """主函数"""
    try:
        # 获取所有命令行参数
        all_args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # 检查参数文件
        if len(all_args) < 1:
            result = {
                "success": False,
                "error": "缺少参数文件",
                "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "in_docker": is_in_docker(),
                "command_args": all_args
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        
        params_file = all_args[0]
        if not os.path.exists(params_file):
            result = {
                "success": False,
                "error": f"参数文件不存在: {params_file}",
                "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "in_docker": is_in_docker(),
                "command_args": all_args
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        
        # 读取参数文件
        with open(params_file, 'r', encoding='utf-8') as f:
            params_data = json.load(f)
        
        # 从标准化的参数结构中提取用户参数
        user_params = params_data.get("user_params", {})
        system_params = params_data.get("system_params", {})
        
        # 在开始时输出用户参数到命令行，方便调试
        print(f"接收到的用户参数: {json.dumps(user_params, ensure_ascii=False, indent=2)}")
        
        # 获取数据库路径
        db_path = find_database()
        if not db_path:
            result = {
                "success": False,
                "error": "无法找到数据库文件",
                "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "in_docker": is_in_docker(),
                "command_args": all_args,
                "user_params": user_params
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 从用户参数中获取表名和数据
        table_name = user_params.get("table_name", "scripts")
        records = user_params.get("records", [])
        
        if not records:
            # 如果未提供记录，创建一个默认记录
            unique_id = str(uuid.uuid4())[:8]
            records = [{
                "name": f"参数脚本 {unique_id}",
                "description": "通过db_insert_with_params_json.py生成的测试数据",
                "file_path": f"scripts/param_test_{unique_id}.py",
                "file_type": "python"
            }]
        
        # 处理插入
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        inserted_ids = []
        inserted_records = []
        
        for record in records:
            # 确保必要字段存在
            name = record.get("name", f"脚本 {str(uuid.uuid4())[:8]}")
            description = record.get("description", "通过参数化脚本创建")
            file_path = record.get("file_path", f"scripts/auto_{str(uuid.uuid4())[:8]}.py")
            file_type = record.get("file_type", "python")
            
            # 执行插入
            if table_name == "scripts":
                cursor.execute('''
                INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, description, file_path, file_type, now, now))
                
                script_id = cursor.lastrowid
                inserted_ids.append(script_id)
                
                # 添加插入的记录详情
                inserted_record = {
                    "id": script_id,
                    "name": name,
                    "description": description,
                    "file_path": file_path,
                    "file_type": file_type,
                    "created_at": now
                }
                inserted_records.append(inserted_record)
                
                # 如果参数中包含脚本参数定义，添加参数
                if "parameters" in record and isinstance(record["parameters"], list):
                    for param in record["parameters"]:
                        param_name = param.get("name", f"param_{str(uuid.uuid4())[:4]}")
                        param_desc = param.get("description", "自动生成的参数")
                        param_type = param.get("param_type", "string")
                        is_required = param.get("is_required", 1)
                        default_value = param.get("default_value")
                        
                        cursor.execute('''
                        INSERT INTO script_parameters
                        (script_id, name, description, param_type, is_required, default_value)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (script_id, param_name, param_desc, param_type, is_required, default_value))
                        
                        param_id = cursor.lastrowid
                        
                        # 添加参数到记录中
                        if "parameters" not in inserted_record:
                            inserted_record["parameters"] = []
                        
                        inserted_record["parameters"].append({
                            "id": param_id,
                            "name": param_name,
                            "description": param_desc,
                            "param_type": param_type,
                            "is_required": is_required,
                            "default_value": default_value
                        })
            else:
                # 处理其他表的情况
                result = {
                    "success": False,
                    "error": f"不支持的表名: {table_name}，目前仅支持'scripts'表",
                    "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "in_docker": is_in_docker(),
                    "command_args": all_args,
                    "user_params": user_params
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
                conn.close()
                return 1
        
        # 提交事务
        conn.commit()
        conn.close()
        
        # 准备输出结果
        result = {
            "success": True,
            "message": f"成功插入 {len(inserted_ids)} 条记录到 {table_name} 表",
            "inserted_ids": inserted_ids,
            "inserted_records": inserted_records,
            "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "in_docker": is_in_docker(),
            "database_path": db_path,
            "command_args": all_args,
            "user_params": user_params,
            "system_params": system_params
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
        
    except sqlite3.Error as e:
        result = {
            "success": False,
            "error": f"数据库错误: {str(e)}",
            "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "in_docker": is_in_docker(),
            "command_args": sys.argv[1:] if len(sys.argv) > 1 else []
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
        
    except Exception as e:
        result = {
            "success": False,
            "error": f"脚本执行出错: {str(e)}",
            "execution_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "in_docker": is_in_docker(),
            "command_args": sys.argv[1:] if len(sys.argv) > 1 else []
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())
