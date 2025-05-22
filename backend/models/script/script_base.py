# -*- coding: utf-8 -*-
"""
脚本基础模型
提供脚本的基本操作
"""
import datetime
import os
import sys
import json

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import logger

# 导入数据库管理器
from ..base import DBManager

class Script:
    """脚本模型类"""
    
    @staticmethod
    def add(name, description, file_path, file_type, url_path=None, output_mode='json'):
        """添加新脚本"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO scripts (name, description, url_path, file_path, file_type, output_mode, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, url_path, file_path, file_type, output_mode, now, now))
            
            script_id = cursor.lastrowid
            
            # 添加初始版本
            try:
                from .script_version import ScriptVersion
                version_id = ScriptVersion.add(script_id, file_path, version="1.0.0", description="初始版本", force_create=True)
                if not version_id:
                    logger.warning(f"添加脚本成功，但创建初始版本失败: 脚本ID {script_id}")
                else:
                    logger.info(f"添加脚本初始版本成功: 脚本ID {script_id}, 版本ID {version_id}")
            except Exception as e:
                logger.error(f"创建脚本初始版本失败: {str(e)}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本成功: {name}")
            return script_id
        except Exception as e:
            logger.error(f"添加脚本失败: {str(e)}")
            return None
    
    @staticmethod
    def update(script_id, name=None, description=None, file_path=None, file_type=None, url_path=None, output_mode=None):
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
            update_url = url_path if url_path is not None else script.get('url_path')
            update_path = file_path if file_path is not None else script['file_path']
            update_type = file_type if file_type is not None else script['file_type']
            update_output_mode = output_mode if output_mode is not None else script.get('output_mode', 'json')
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE scripts
            SET name = ?, description = ?, url_path = ?, file_path = ?, file_type = ?, output_mode = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_url, update_path, update_type, update_output_mode, now, script_id))
            
            # 如果文件路径改变，则添加新版本
            if file_path and file_path != script['file_path']:
                # 添加新版本
                from .script_version import ScriptVersion
                ScriptVersion.add(script_id, file_path, description="更新文件", force_create=True)
            
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
                from .script_parameter import ScriptParameter
                params = ScriptParameter.get_by_script(script_id)
                script['parameters'] = params
                
                # 获取脚本版本
                from .script_version import ScriptVersion
                versions = ScriptVersion.get_versions(script_id)
                script['versions'] = versions
                
                # 获取当前版本
                cursor.execute('''
                SELECT * FROM script_versions
                WHERE script_id = ? AND is_current = 1
                ''', (script_id,))
                
                current_version = cursor.fetchone()
                if current_version:
                    script['current_version'] = current_version['version']
                    script['file_path'] = current_version['file_path']
            
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
            SELECT s.*, 
                   (SELECT COUNT(*) FROM script_versions WHERE script_id = s.id) as version_count,
                   (SELECT version FROM script_versions WHERE script_id = s.id AND is_current = 1) as current_version
            FROM scripts s
            WHERE s.is_deleted = 0
            ORDER BY s.created_at DESC
            ''')
            
            scripts = cursor.fetchall()
            conn.close()
            return scripts
        except Exception as e:
            logger.error(f"获取脚本列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_by_url_path(url_path):
        """根据URL路径获取脚本"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM scripts
            WHERE url_path = ? AND is_deleted = 0
            ''', (url_path,))
            
            scripts = cursor.fetchall()
            
            # 为每个脚本添加版本信息
            for script in scripts:
                # 获取脚本版本
                from .script_version import ScriptVersion
                versions = ScriptVersion.get_versions(script['id'])
                script['versions'] = versions
                
                # 获取当前版本
                cursor.execute('''
                SELECT * FROM script_versions
                WHERE script_id = ? AND is_current = 1
                ''', (script['id'],))
                
                current_version = cursor.fetchone()
                if current_version:
                    script['current_version'] = current_version['version']
                    script['file_path'] = current_version['file_path']
            
            conn.close()
            return scripts
        except Exception as e:
            logger.error(f"根据URL路径获取脚本失败: {str(e)}")
            return []
    
    @staticmethod
    def set_version_current(script_id, version_id):
        """设置脚本的当前版本"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            # 检查版本是否存在
            cursor.execute('''
            SELECT * FROM script_versions
            WHERE id = ? AND script_id = ?
            ''', (version_id, script_id))
            
            version = cursor.fetchone()
            if not version:
                conn.close()
                return False
            
            # 将所有版本设置为非当前版本
            cursor.execute('''
            UPDATE script_versions
            SET is_current = 0
            WHERE script_id = ?
            ''', (script_id,))
            
            # 将指定版本设置为当前版本
            cursor.execute('''
            UPDATE script_versions
            SET is_current = 1
            WHERE id = ?
            ''', (version_id,))
            
            # 更新脚本文件路径为当前版本的文件路径
            cursor.execute('''
            UPDATE scripts
            SET file_path = ?
            WHERE id = ?
            ''', (version['file_path'], script_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"设置脚本当前版本成功: 脚本ID {script_id}, 版本ID {version_id}")
            return True
        except Exception as e:
            logger.error(f"设置脚本当前版本失败: {str(e)}")
            return False
    
    @staticmethod
    def update_parameters(script_id, parameters):
        """更新脚本参数
        
        Args:
            script_id: 脚本ID
            parameters: 参数列表，每个参数是一个字典，包含name, description, param_type, is_required, default_value
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            # 检查脚本是否存在
            cursor.execute("SELECT * FROM scripts WHERE id = ? AND is_deleted = 0", (script_id,))
            script = cursor.fetchone()
            
            if not script:
                logger.error(f"更新脚本参数失败: 脚本ID {script_id} 不存在")
                conn.close()
                return False
            
            # 获取脚本当前的参数
            cursor.execute("SELECT * FROM script_parameters WHERE script_id = ?", (script_id,))
            current_params = cursor.fetchall()
            
            # 删除所有现有参数
            cursor.execute("DELETE FROM script_parameters WHERE script_id = ?", (script_id,))
            
            # 添加新参数
            from .script_parameter import ScriptParameter
            for param in parameters:
                name = param.get('name', '')
                description = param.get('description', '')
                param_type = param.get('param_type', 'string')
                is_required = int(param.get('is_required', 0))
                default_value = param.get('default_value', '')
                
                cursor.execute('''
                INSERT INTO script_parameters
                (script_id, name, description, param_type, is_required, default_value)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (script_id, name, description, param_type, is_required, default_value))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新脚本参数成功: 脚本ID {script_id}")
            return True
        except Exception as e:
            logger.error(f"更新脚本参数失败: {str(e)}")
            return False
