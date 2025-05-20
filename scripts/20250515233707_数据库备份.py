#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库备份脚本
备份SQLite数据库到指定位置
"""
import os
import sys
import json
import shutil
import datetime
import sqlite3
import zipfile

def backup_sqlite_db(db_path, backup_dir=None, compress=True):
    """备份SQLite数据库"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    # 设置备份目录
    if not backup_dir:
        backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    
    # 创建备份目录（如果不存在）
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    db_name = os.path.basename(db_path)
    backup_name = f"{os.path.splitext(db_name)[0]}_{timestamp}.sqlite"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 复制数据库文件
    shutil.copy2(db_path, backup_path)
    
    # 如果需要压缩
    zip_path = None
    if compress:
        zip_name = f"{os.path.splitext(db_name)[0]}_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, arcname=backup_name)
        
        # 删除未压缩的备份
        os.remove(backup_path)
        backup_path = zip_path
    
    # 生成结果
    result = {
        "original_db": db_path,
        "backup_path": backup_path,
        "backup_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "compressed": compress
    }
    
    return result

def main():
    """主函数"""
    try:
        # 处理参数
        params_file = None
        if len(sys.argv) > 1:
            params_file = sys.argv[1]
        
        # 读取参数文件
        params = {}
        if params_file and os.path.exists(params_file):
            with open(params_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
        
        # 获取参数
        db_path = params.get('db_path')
        if not db_path:
            # 如果没有提供数据库路径，则使用默认的项目数据库
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            db_path = os.path.join(project_root, 'database', 'scripts.db')
        
        backup_dir = params.get('backup_dir')
        compress = params.get('compress', True)
        
        # 备份数据库
        result = backup_sqlite_db(db_path, backup_dir, compress)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
