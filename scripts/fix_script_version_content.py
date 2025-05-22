#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复脚本版本内容

此脚本用于检查和修复前端无法查看脚本内容的问题。
主要检查以下几个方面：
1. 验证数据库中存储的文件路径是否存在
2. 如果文件路径有问题，将脚本内容直接存储在数据库中
3. 提供创建临时版本文件的功能
"""

import os
import sys
import json
import datetime
import sqlite3
import tempfile

# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 导入数据库模型类
from backend.models.script.script_version import ScriptVersion
from backend.models import Script, DBManager
from config import DATABASE_PATH, logger

def main():
    """主函数"""
    print(json.dumps({
        "status": "开始",
        "message": "开始检查和修复脚本版本内容",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 要检查的脚本文件
    script_files = [
        "scripts/chain_test_1_generate.py",
        "scripts/chain_test_2_process.py",
        "scripts/chain_test_3_report.py"
    ]
    
    # 获取数据库中的脚本信息
    scripts = get_scripts_by_file_paths(script_files)
    
    if not scripts:
        print(json.dumps({
            "status": "错误",
            "message": "数据库中未找到相关脚本",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return 1
    
    # 检查脚本版本内容
    for script in scripts:
        check_and_fix_script_content(script)
    
    # 添加数据库内容字段
    add_content_column_if_not_exists()
    
    # 输出总结信息
    print(json.dumps({
        "status": "完成",
        "message": "脚本版本内容检查和修复完成",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    return 0

def get_scripts_by_file_paths(file_paths):
    """根据文件路径获取脚本信息"""
    try:
        conn = DBManager.get_connection()
        conn.row_factory = DBManager.dict_factory
        cursor = conn.cursor()
        
        # 构建查询条件
        placeholders = ", ".join(["?" for _ in file_paths])
        query = f"SELECT * FROM scripts WHERE file_path IN ({placeholders}) AND is_deleted = 0"
        
        cursor.execute(query, file_paths)
        scripts = cursor.fetchall()
        
        conn.close()
        return scripts
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"获取脚本信息失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return []

def check_and_fix_script_content(script):
    """检查和修复脚本版本内容"""
    script_id = script["id"]
    script_name = script["name"]
    file_path = script["file_path"]
    
    print(json.dumps({
        "status": "进行中",
        "message": f"检查脚本 '{script_name}' (ID: {script_id}) 的版本内容",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 获取版本信息
    versions = get_version_details(script_id)
    
    if not versions:
        print(json.dumps({
            "status": "警告",
            "message": f"脚本 '{script_name}' (ID: {script_id}) 没有版本信息",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return
    
    for version in versions:
        version_id = version["id"]
        version_path = version["file_path"]
        
        # 检查文件路径是否存在
        file_exists = os.path.exists(version_path)
        
        # 获取脚本内容
        content = None
        if file_exists:
            try:
                with open(version_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(json.dumps({
                    "status": "信息",
                    "message": f"版本 ID {version_id} 的文件存在并可读取: {version_path}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
            except Exception as e:
                print(json.dumps({
                    "status": "警告",
                    "message": f"版本 ID {version_id} 的文件虽然存在但无法读取: {version_path}, 错误: {str(e)}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                content = None
        else:
            # 尝试从原始脚本文件读取内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(json.dumps({
                    "status": "信息",
                    "message": f"版本 ID {version_id} 的文件不存在: {version_path}，但从原始文件读取成功: {file_path}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
            except Exception as e:
                print(json.dumps({
                    "status": "警告",
                    "message": f"版本 ID {version_id} 的文件不存在: {version_path}，且无法从原始文件读取: {file_path}, 错误: {str(e)}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                content = None
        
        if content:
            # 将内容存储到数据库
            store_content_in_db(version_id, content)
            
            # 创建临时版本文件
            tmp_dir = tempfile.gettempdir()
            tmp_file_path = os.path.join(tmp_dir, f"script_version_{version_id}.py")
            
            try:
                with open(tmp_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新数据库中的文件路径
                update_version_file_path(version_id, tmp_file_path)
                
                print(json.dumps({
                    "status": "成功",
                    "message": f"已为版本 ID {version_id} 创建临时文件: {tmp_file_path}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
            except Exception as e:
                print(json.dumps({
                    "status": "错误",
                    "message": f"创建临时文件失败: {str(e)}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))

def get_version_details(script_id):
    """获取脚本的版本详情"""
    try:
        conn = DBManager.get_connection()
        conn.row_factory = DBManager.dict_factory
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM script_versions
        WHERE script_id = ?
        ORDER BY id
        ''', (script_id,))
        
        versions = cursor.fetchall()
        conn.close()
        
        return versions
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"获取脚本版本详情失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return []

def update_version_file_path(version_id, new_file_path):
    """更新版本的文件路径"""
    try:
        conn = DBManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE script_versions
        SET file_path = ?
        WHERE id = ?
        ''', (new_file_path, version_id))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"更新版本文件路径失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return False

def add_content_column_if_not_exists():
    """检查并添加脚本内容字段到版本表"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 检查content列是否存在
        cursor.execute("PRAGMA table_info(script_versions)")
        columns = cursor.fetchall()
        
        has_content_column = any(col[1] == "content" for col in columns)
        
        if not has_content_column:
            # 添加content列
            cursor.execute("ALTER TABLE script_versions ADD COLUMN content TEXT")
            conn.commit()
            
            print(json.dumps({
                "status": "信息",
                "message": "向script_versions表添加content列成功",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "status": "信息",
                "message": "script_versions表已存在content列",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        
        conn.close()
        return True
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"添加content列失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return False

def store_content_in_db(version_id, content):
    """将脚本内容直接存储到数据库中"""
    try:
        conn = DBManager.get_connection()
        cursor = conn.cursor()
        
        # 检查是否已添加content列
        try:
            cursor.execute('''
            UPDATE script_versions
            SET content = ?
            WHERE id = ?
            ''', (content, version_id))
            
            conn.commit()
            
            print(json.dumps({
                "status": "信息",
                "message": f"脚本内容已存储到数据库中: 版本ID {version_id}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        except sqlite3.OperationalError as e:
            if "no such column: content" in str(e):
                print(json.dumps({
                    "status": "警告",
                    "message": "script_versions表中没有content列，请先添加该列",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
            else:
                raise e
        
        conn.close()
        return True
    except Exception as e:
        print(json.dumps({
            "status": "错误",
            "message": f"将脚本内容存储到数据库失败: {str(e)}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return False

def modify_get_file_content_method():
    """创建修改后的获取文件内容方法的代码"""
    modified_code = '''
@staticmethod
def get_file_content(version_id):
    """获取指定版本的文件内容"""
    try:
        version = ScriptVersion.get_version_by_id(version_id)
        if not version:
            return None
            
        # 优先从数据库中读取内容
        conn = DBManager.get_connection()
        conn.row_factory = DBManager.dict_factory
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT content FROM script_versions WHERE id = ?", (version_id,))
            result = cursor.fetchone()
            if result and result['content']:
                logger.info(f"从数据库中读取脚本内容成功: 版本ID {version_id}")
                conn.close()
                return result['content']
        except sqlite3.OperationalError as e:
            # 如果没有content列，则忽略错误
            pass
        
        conn.close()
            
        # 如果数据库中没有内容，则尝试从文件中读取
        if not version['file_path']:
            return None
            
        # 读取文件内容
        try:
            with open(version['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"从文件中读取脚本内容成功: {version['file_path']}")
            return content
        except Exception as e:
            logger.error(f"读取脚本文件失败: {str(e)}")
            
            # 如果指定文件读取失败，尝试从脚本原始文件读取
            script = Script.get(version['script_id'])
            if script and script['file_path'] and os.path.exists(script['file_path']):
                try:
                    with open(script['file_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    logger.info(f"从原始脚本文件中读取内容成功: {script['file_path']}")
                    return content
                except Exception as e2:
                    logger.error(f"读取原始脚本文件失败: {str(e2)}")
            
            return None
    except Exception as e:
        logger.error(f"获取脚本版本文件内容失败: {str(e)}")
        return None
'''
    
    print(json.dumps({
        "status": "信息",
        "message": "建议修改ScriptVersion.get_file_content方法，使其优先从数据库中读取内容",
        "modified_code": modified_code,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
    # 输出修改建议
    modify_get_file_content_method()
