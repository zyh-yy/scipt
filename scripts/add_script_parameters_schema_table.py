#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加script_parameters_schema表
此脚本用于创建存储脚本参数模式(schema)的表结构
"""
import os
import sys
import sqlite3
import json
import datetime

# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)

# 导入项目配置
from backend.config import DB_PATH, logger

def create_tables():
    """创建脚本参数模式相关表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='script_parameters_schema'")
        if cursor.fetchone():
            logger.info("表 script_parameters_schema 已存在，跳过创建")
            conn.close()
            return True
        
        # 创建script_parameters_schema表
        cursor.execute('''
        CREATE TABLE script_parameters_schema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_id INTEGER NOT NULL,
            schema TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (script_id) REFERENCES scripts(id)
        )
        ''')
        
        # 添加索引
        cursor.execute('CREATE INDEX idx_script_parameters_schema_script_id ON script_parameters_schema(script_id)')
        
        # 在script_parameters表中添加validation_rules字段（如果表存在）
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='script_parameters'")
        if cursor.fetchone():
            # 检查字段是否已存在
            cursor.execute("PRAGMA table_info(script_parameters)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'validation_rules' not in columns:
                cursor.execute('ALTER TABLE script_parameters ADD COLUMN validation_rules TEXT')
                logger.info("在script_parameters表中添加了validation_rules字段")
        
        conn.commit()
        conn.close()
        
        logger.info("成功创建script_parameters_schema表")
        return True
    except Exception as e:
        logger.error(f"创建表失败: {str(e)}")
        return False

def generate_default_schemas():
    """为现有脚本生成默认参数模式"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取所有脚本
        cursor.execute("SELECT id, name FROM scripts")
        scripts = cursor.fetchall()
        
        # 为每个脚本创建默认模式
        for script in scripts:
            script_id = script['id']
            script_name = script['name']
            
            # 检查是否已有模式
            cursor.execute("SELECT COUNT(*) FROM script_parameters_schema WHERE script_id = ?", (script_id,))
            if cursor.fetchone()[0] > 0:
                continue
            
            # 获取脚本参数
            cursor.execute('''
            SELECT name, description, param_type, is_required, default_value, validation_rules
            FROM script_parameters
            WHERE script_id = ?
            ''', (script_id,))
            
            params = cursor.fetchall()
            
            # 创建默认模式
            schema = {
                "parameters": []
            }
            
            # 添加参数定义
            for param in params:
                param_def = {
                    "name": param['name'],
                    "description": param['description'],
                    "type": param['param_type'],
                    "required": bool(param['is_required']),
                    "default": param['default_value']
                }
                
                # 添加验证规则（如果有）
                if param['validation_rules']:
                    try:
                        validation = json.loads(param['validation_rules'])
                        param_def.update(validation)
                    except:
                        pass
                
                schema["parameters"].append(param_def)
            
            # 保存模式
            schema_json = json.dumps(schema, ensure_ascii=False)
            cursor.execute('''
            INSERT INTO script_parameters_schema
            (script_id, schema, created_at, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (script_id, schema_json))
            
            logger.info(f"为脚本 '{script_name}' (ID: {script_id}) 创建了默认参数模式")
        
        conn.commit()
        conn.close()
        
        logger.info("成功生成默认参数模式")
        return True
    except Exception as e:
        logger.error(f"生成默认参数模式失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始数据库迁移...")
    
    # 创建表
    if not create_tables():
        print("创建表失败，迁移终止")
        return 1
    
    # 生成默认模式
    if not generate_default_schemas():
        print("生成默认参数模式失败")
        return 1
    
    print("数据库迁移完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
