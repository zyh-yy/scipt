"""
简化的数据库初始化脚本 - 仅创建空数据库
"""
import os
import sqlite3
import sys

def create_empty_database():
    """创建一个空的SQLite数据库文件"""
    # 获取当前工作目录（frame目录）
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, "script_platform.db")
    
    print(f"数据库路径: {db_path}")
    
    # 如果数据库文件已存在，则删除它
    if os.path.exists(db_path):
        print(f"删除现有数据库文件: {db_path}")
        os.remove(db_path)
    
    # 创建一个新的空数据库
    print(f"创建新的空数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    
    # 创建一个简单的测试表以验证数据库是否正常工作
    print("创建测试表...")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chains (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        steps TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS executions (
        id TEXT PRIMARY KEY,
        script_id TEXT,
        chain_id TEXT,
        status TEXT NOT NULL,
        result TEXT,
        error TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        parameters TEXT
    )
    ''')
    
    conn.commit()
    
    # 验证表格已创建
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\"'table'\";")
    tables = cursor.fetchall()
    
    print("已创建的表格:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 关闭连接
    conn.close()
    
    print("数据库初始化完成")
    return db_path

if __name__ == "__main__":
    db_path = create_empty_database()
print(f"数据库已初始化: {db_path}")
    print(f"数据库已初始化: {db_path}")
print(f"数据库已初始化: {db_path}")
    print(f"数据库已初始化: {db_path}")
