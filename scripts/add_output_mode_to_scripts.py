#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板功能数据库迁移脚本
为scripts表添加output_mode字段
"""
import os
import sys
import sqlite3
from pathlib import Path

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.config import logger, DATABASE_PATH

def main():
    """主函数"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(scripts)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'output_mode' not in column_names:
            # 添加output_mode字段
            cursor.execute("ALTER TABLE scripts ADD COLUMN output_mode VARCHAR(10) DEFAULT 'json'")
            conn.commit()
            print("成功向scripts表添加output_mode字段")
            logger.info("成功向scripts表添加output_mode字段")
        else:
            print("output_mode字段已存在")
            logger.info("output_mode字段已存在")
        
        # 关闭连接
        conn.close()
        return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        logger.error(f"添加output_mode字段失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
