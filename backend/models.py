# -*- coding: utf-8 -*-
"""
数据库模型
定义应用所需的数据库表结构
"""
import os
import json
import sqlite3
import datetime
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
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_deleted INTEGER DEFAULT 0
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
            FOREIGN KEY (script_id) REFERENCES scripts (id),
            FOREIGN KEY (chain_id) REFERENCES script_chains (id)
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

class Script:
    """脚本模型类"""
    
    @staticmethod
    def add(name, description, file_path, file_type):
        """添加新脚本"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO scripts (name, description, file_path, file_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, file_path, file_type, now, now))
            
            script_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本成功: {name}")
            return script_id
        except Exception as e:
            logger.error(f"添加脚本失败: {str(e)}")
            return None
    
    @staticmethod
    def update(script_id, name=None, description=None, file_path=None, file_type=None):
        """更新脚本信息"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前脚本信息
            cursor.execute("SELECT * FROM scripts WHERE id = ? AND is_deleted = 0", (script_id,))
            script = cursor.fetchone()
            
            if not script:
                logger.error(f"更新脚本失败: 脚本ID {script_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_name = name if name is not None else script['name']
            update_desc = description if description is not None else script['description']
            update_path = file_path if file_path is not None else script['file_path']
            update_type = file_type if file_type is not None else script['file_type']
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE scripts
            SET name = ?, description = ?, file_path = ?, file_type = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_path, update_type, now, script_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新脚本成功: ID {script_id}")
            return True
        except Exception as e:
            logger.error(f"更新脚本失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(script_id):
        """软删除脚本"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE scripts
            SET is_deleted = 1, updated_at = ?
            WHERE id = ?
            ''', (now, script_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除脚本成功: ID {script_id}")
            return True
        except Exception as e:
            logger.error(f"删除脚本失败: {str(e)}")
            return False
    
    @staticmethod
    def get(script_id):
        """获取脚本详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM scripts
            WHERE id = ? AND is_deleted = 0
            ''', (script_id,))
            
            script = cursor.fetchone()
            
            if script:
                # 获取脚本参数
                cursor.execute('''
                SELECT * FROM script_parameters
                WHERE script_id = ?
                ORDER BY id
                ''', (script_id,))
                
                params = cursor.fetchall()
                script['parameters'] = params
            
            conn.close()
            return script
        except Exception as e:
            logger.error(f"获取脚本失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        """获取所有非删除的脚本"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM scripts
            WHERE is_deleted = 0
            ORDER BY created_at DESC
            ''')
            
            scripts = cursor.fetchall()
            conn.close()
            return scripts
        except Exception as e:
            logger.error(f"获取脚本列表失败: {str(e)}")
            return []

class ScriptParameter:
    """脚本参数模型类"""
    
    @staticmethod
    def add(script_id, name, description, param_type, is_required=1, default_value=None):
        """添加脚本参数"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO script_parameters
            (script_id, name, description, param_type, is_required, default_value)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (script_id, name, description, param_type, is_required, default_value))
            
            param_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本参数成功: {name} 属于脚本ID {script_id}")
            return param_id
        except Exception as e:
            logger.error(f"添加脚本参数失败: {str(e)}")
            return None
    
    @staticmethod
    def update(param_id, name=None, description=None, param_type=None, is_required=None, default_value=None):
        """更新脚本参数"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前参数信息
            cursor.execute("SELECT * FROM script_parameters WHERE id = ?", (param_id,))
            param = cursor.fetchone()
            
            if not param:
                logger.error(f"更新脚本参数失败: 参数ID {param_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_name = name if name is not None else param['name']
            update_desc = description if description is not None else param['description']
            update_type = param_type if param_type is not None else param['param_type']
            update_required = is_required if is_required is not None else param['is_required']
            update_default = default_value if default_value is not None else param['default_value']
            
            cursor.execute('''
            UPDATE script_parameters
            SET name = ?, description = ?, param_type = ?, is_required = ?, default_value = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_type, update_required, update_default, param_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新脚本参数成功: ID {param_id}")
            return True
        except Exception as e:
            logger.error(f"更新脚本参数失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(param_id):
        """删除脚本参数"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM script_parameters WHERE id = ?", (param_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除脚本参数成功: ID {param_id}")
            return True
        except Exception as e:
            logger.error(f"删除脚本参数失败: {str(e)}")
            return False
    
    @staticmethod
    def get_by_script(script_id):
        """获取脚本的所有参数"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_parameters
            WHERE script_id = ?
            ORDER BY id
            ''', (script_id,))
            
            params = cursor.fetchall()
            conn.close()
            return params
        except Exception as e:
            logger.error(f"获取脚本参数失败: {str(e)}")
            return []

class ScriptChain:
    """脚本链模型类"""
    
    @staticmethod
    def add(name, description):
        """添加脚本链"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO script_chains (name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (name, description, now, now))
            
            chain_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本链成功: {name}")
            return chain_id
        except Exception as e:
            logger.error(f"添加脚本链失败: {str(e)}")
            return None
    
    @staticmethod
    def update(chain_id, name=None, description=None):
        """更新脚本链信息"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前脚本链信息
            cursor.execute("SELECT * FROM script_chains WHERE id = ? AND is_deleted = 0", (chain_id,))
            chain = cursor.fetchone()
            
            if not chain:
                logger.error(f"更新脚本链失败: 链ID {chain_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_name = name if name is not None else chain['name']
            update_desc = description if description is not None else chain['description']
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE script_chains
            SET name = ?, description = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, now, chain_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新脚本链成功: ID {chain_id}")
            return True
        except Exception as e:
            logger.error(f"更新脚本链失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(chain_id):
        """软删除脚本链"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE script_chains
            SET is_deleted = 1, updated_at = ?
            WHERE id = ?
            ''', (now, chain_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除脚本链成功: ID {chain_id}")
            return True
        except Exception as e:
            logger.error(f"删除脚本链失败: {str(e)}")
            return False
    
    @staticmethod
    def get(chain_id):
        """获取脚本链详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_chains
            WHERE id = ? AND is_deleted = 0
            ''', (chain_id,))
            
            chain = cursor.fetchone()
            
            if chain:
                # 获取脚本链节点
                cursor.execute('''
                SELECT cn.*, s.name as script_name, s.file_type
                FROM chain_nodes cn
                JOIN scripts s ON cn.script_id = s.id
                WHERE cn.chain_id = ? AND s.is_deleted = 0
                ORDER BY cn.node_order
                ''', (chain_id,))
                
                nodes = cursor.fetchall()
                chain['nodes'] = nodes
            
            conn.close()
            return chain
        except Exception as e:
            logger.error(f"获取脚本链失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all():
        """获取所有非删除的脚本链"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_chains
            WHERE is_deleted = 0
            ORDER BY created_at DESC
            ''')
            
            chains = cursor.fetchall()
            conn.close()
            return chains
        except Exception as e:
            logger.error(f"获取脚本链列表失败: {str(e)}")
            return []

class ChainNode:
    """脚本链节点模型类"""
    
    @staticmethod
    def add(chain_id, script_id, node_order):
        """添加脚本链节点"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO chain_nodes (chain_id, script_id, node_order)
            VALUES (?, ?, ?)
            ''', (chain_id, script_id, node_order))
            
            node_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本链节点成功: 链ID {chain_id}, 脚本ID {script_id}, 序号 {node_order}")
            return node_id
        except Exception as e:
            logger.error(f"添加脚本链节点失败: {str(e)}")
            return None
    
    @staticmethod
    def update_order(node_id, new_order):
        """更新节点顺序"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE chain_nodes
            SET node_order = ?
            WHERE id = ?
            ''', (new_order, node_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新脚本链节点顺序成功: ID {node_id}, 新序号 {new_order}")
            return True
        except Exception as e:
            logger.error(f"更新脚本链节点顺序失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(node_id):
        """删除脚本链节点"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM chain_nodes WHERE id = ?", (node_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除脚本链节点成功: ID {node_id}")
            return True
        except Exception as e:
            logger.error(f"删除脚本链节点失败: {str(e)}")
            return False
    
    @staticmethod
    def get_by_chain(chain_id):
        """获取脚本链的所有节点"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT cn.*, s.name as script_name, s.file_type, s.description as script_description
            FROM chain_nodes cn
            JOIN scripts s ON cn.script_id = s.id
            WHERE cn.chain_id = ? AND s.is_deleted = 0
            ORDER BY cn.node_order
            ''', (chain_id,))
            
            nodes = cursor.fetchall()
            conn.close()
            return nodes
        except Exception as e:
            logger.error(f"获取脚本链节点失败: {str(e)}")
            return []

class ExecutionHistory:
    """执行历史模型类"""
    
    @staticmethod
    def add(script_id=None, chain_id=None, status="running", params=None, output=None, error=None):
        """添加执行历史记录"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            params_json = json.dumps(params) if params else None
            
            cursor.execute('''
            INSERT INTO execution_history
            (script_id, chain_id, status, start_time, params, output, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (script_id, chain_id, status, now, params_json, output, error))
            
            history_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加执行历史记录成功: 脚本ID {script_id}, 链ID {chain_id}")
            return history_id
        except Exception as e:
            logger.error(f"添加执行历史记录失败: {str(e)}")
            return None
    
    @staticmethod
    def update(history_id, status=None, output=None, error=None):
        """更新执行历史记录"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前记录
            cursor.execute("SELECT * FROM execution_history WHERE id = ?", (history_id,))
            history = cursor.fetchone()
            
            if not history:
                logger.error(f"更新执行历史记录失败: 记录ID {history_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_status = status if status is not None else history['status']
            update_output = output if output is not None else history['output']
            update_error = error if error is not None else history['error']
            
            # 如果状态是已完成或失败，更新结束时间
            end_time = None
            if status in ["completed", "failed"]:
                end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                UPDATE execution_history
                SET status = ?, output = ?, error = ?, end_time = ?
                WHERE id = ?
                ''', (update_status, update_output, update_error, end_time, history_id))
            else:
                cursor.execute('''
                UPDATE execution_history
                SET status = ?, output = ?, error = ?
                WHERE id = ?
                ''', (update_status, update_output, update_error, history_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新执行历史记录成功: ID {history_id}")
            return True
        except Exception as e:
            logger.error(f"更新执行历史记录失败: {str(e)}")
            return False
    
    @staticmethod
    def get(history_id):
        """获取执行历史记录详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM execution_history
            WHERE id = ?
            ''', (history_id,))
            
            history = cursor.fetchone()
            
            if history and history['params']:
                try:
                    history['params'] = json.loads(history['params'])
                except:
                    pass
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"获取执行历史记录失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all(limit=50):
        """获取最近的执行历史记录"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT 
                h.*, 
                s.name as script_name,
                c.name as chain_name
            FROM execution_history h
            LEFT JOIN scripts s ON h.script_id = s.id
            LEFT JOIN script_chains c ON h.chain_id = c.id
            ORDER BY h.start_time DESC
            LIMIT ?
            ''', (limit,))
            
            histories = cursor.fetchall()
            
            # 解析参数JSON
            for history in histories:
                if history['params']:
                    try:
                        history['params'] = json.loads(history['params'])
                    except:
                        pass
            
            conn.close()
            return histories
        except Exception as e:
            logger.error(f"获取执行历史记录列表失败: {str(e)}")
            return []
