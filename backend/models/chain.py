# -*- coding: utf-8 -*-
"""
脚本链模型模块
定义脚本链相关数据库模型和操作
"""
import datetime
import json
from .base import DBManager
from config import logger

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
            SELECT sc.*, 
                  (SELECT COUNT(*) FROM chain_nodes WHERE chain_id = sc.id) as node_count,
                  (SELECT COUNT(*) FROM execution_history WHERE chain_id = sc.id) as execution_count
            FROM script_chains sc
            WHERE sc.is_deleted = 0
            ORDER BY sc.created_at DESC
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
