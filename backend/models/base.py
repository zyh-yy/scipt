# -*- coding: utf-8 -*-
"""
数据库基础模块
提供数据库连接和基础操作功能
"""
import os
import sqlite3
from config import DATABASE_PATH, logger

def initialize_db():
    """初始化数据库"""
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 创建脚本表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            url_path TEXT,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
        ''')
        
        # 创建脚本版本表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS script_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_id INTEGER NOT NULL,
            version TEXT NOT NULL,
            file_path TEXT NOT NULL,
            is_current INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (script_id) REFERENCES scripts (id)
        )
        ''')
        
        # 创建脚本参数表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS script_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            param_type TEXT NOT NULL,
            is_required INTEGER DEFAULT 1,
            default_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (script_id) REFERENCES scripts (id)
        )
        ''')
        
        # 创建脚本链表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS script_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
        )
        ''')
        
        # 创建脚本链节点表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chain_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER NOT NULL,
            script_id INTEGER NOT NULL,
            node_order INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chain_id) REFERENCES script_chains (id),
            FOREIGN KEY (script_id) REFERENCES scripts (id)
        )
        ''')
        
        # 创建执行历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script_id INTEGER,
            chain_id INTEGER,
            status TEXT NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            params TEXT,
            output TEXT,
            error TEXT,
            execution_time REAL,
            FOREIGN KEY (script_id) REFERENCES scripts (id),
            FOREIGN KEY (chain_id) REFERENCES script_chains (id)
        )
        ''')
        
        # 创建定时任务表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            script_id INTEGER,
            chain_id INTEGER,
            schedule_type TEXT NOT NULL,
            cron_expression TEXT,
            params TEXT,
            is_active INTEGER DEFAULT 1,
            last_run TIMESTAMP,
            next_run TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (script_id) REFERENCES scripts (id),
            FOREIGN KEY (chain_id) REFERENCES script_chains (id)
        )
        ''')
        
        # 创建告警配置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            alert_type TEXT NOT NULL,
            condition_type TEXT NOT NULL,
            condition_value TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            notification_config TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建告警历史表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_config_id INTEGER NOT NULL,
            execution_id INTEGER,
            status TEXT NOT NULL,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alert_config_id) REFERENCES alert_configs (id),
            FOREIGN KEY (execution_id) REFERENCES execution_history (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化成功")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

class DBManager:
    """数据库管理类"""
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.row_factory = sqlite3.Row  # 设置行工厂，使查询结果可以通过列名访问
            return conn
        except Exception as e:
            logger.error(f"获取数据库连接失败: {str(e)}")
            return None
    
    @staticmethod
    def dict_factory(cursor, row):
        """将查询结果转换为字典"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
