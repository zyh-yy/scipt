# -*- coding: utf-8 -*-
"""
脚本参数模型
提供脚本参数的操作和管理
"""
import os
import sys
import datetime

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import logger

# 导入数据库管理器
from ..base import DBManager

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
