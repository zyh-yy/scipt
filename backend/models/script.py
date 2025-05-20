# -*- coding: utf-8 -*-
"""
脚本模型模块
定义脚本相关数据库模型和操作
"""
import datetime
import json
import os
import sys
from .base import DBManager

# Use the same approach for importing config as in base.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger

class Script:
    """脚本模型类"""
    
    @staticmethod
    def add(name, description, file_path, file_type, url_path=None):
        """添加新脚本"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO scripts (name, description, url_path, file_path, file_type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, url_path, file_path, file_type, now, now))
            
            script_id = cursor.lastrowid
            
            # 添加初始版本
            version = "1.0.0"
            cursor.execute('''
            INSERT INTO script_versions (script_id, version, file_path, is_current)
            VALUES (?, ?, ?, 1)
            ''', (script_id, version, file_path))
            
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本成功: {name}")
            return script_id
        except Exception as e:
            logger.error(f"添加脚本失败: {str(e)}")
            return None
    
    @staticmethod
    def update(script_id, name=None, description=None, file_path=None, file_type=None, url_path=None):
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
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE scripts
            SET name = ?, description = ?, url_path = ?, file_path = ?, file_type = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_url, update_path, update_type, now, script_id))
            
            # 如果文件路径改变，则添加新版本
            if file_path and file_path != script['file_path']:
                # 获取最新版本
                cursor.execute('''
                SELECT version FROM script_versions 
                WHERE script_id = ? ORDER BY id DESC LIMIT 1
                ''', (script_id,))
                latest_version = cursor.fetchone()
                
                # 计算新版本号
                if latest_version:
                    version_parts = latest_version['version'].split('.')
                    new_version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
                else:
                    new_version = "1.0.0"
                
                # 将所有现有版本标记为非当前版本
                cursor.execute('''
                UPDATE script_versions SET is_current = 0 WHERE script_id = ?
                ''', (script_id,))
                
                # 添加新版本
                cursor.execute('''
                INSERT INTO script_versions (script_id, version, file_path, is_current)
                VALUES (?, ?, ?, 1)
                ''', (script_id, new_version, file_path))
            
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
                
                # 获取脚本版本
                cursor.execute('''
                SELECT * FROM script_versions
                WHERE script_id = ?
                ORDER BY id DESC
                ''', (script_id,))
                
                versions = cursor.fetchall()
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
                cursor.execute('''
                SELECT * FROM script_versions
                WHERE script_id = ?
                ORDER BY id DESC
                ''', (script['id'],))
                
                versions = cursor.fetchall()
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


class ScriptVersion:
    """脚本版本模型类"""
    
    @staticmethod
    def add(script_id, file_path, version=None):
        """添加脚本版本"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取最新版本
            cursor.execute('''
            SELECT version FROM script_versions 
            WHERE script_id = ? ORDER BY id DESC LIMIT 1
            ''', (script_id,))
            latest_version = cursor.fetchone()
            
            # 计算新版本号
            if not version:
                if latest_version:
                    version_parts = latest_version['version'].split('.')
                    version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
                else:
                    version = "1.0.0"
            
            # 将所有现有版本标记为非当前版本
            cursor.execute('''
            UPDATE script_versions SET is_current = 0 WHERE script_id = ?
            ''', (script_id,))
            
            # 添加新版本
            cursor.execute('''
            INSERT INTO script_versions (script_id, version, file_path, is_current)
            VALUES (?, ?, ?, 1)
            ''', (script_id, version, file_path))
            
            version_id = cursor.lastrowid
            
            # 更新脚本的文件路径
            cursor.execute('''
            UPDATE scripts SET file_path = ? WHERE id = ?
            ''', (file_path, script_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本版本成功: 脚本ID {script_id}, 版本 {version}")
            return version_id
        except Exception as e:
            logger.error(f"添加脚本版本失败: {str(e)}")
            return None
    
    @staticmethod
    def get_versions(script_id):
        """获取脚本的所有版本"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_versions
            WHERE script_id = ?
            ORDER BY id DESC
            ''', (script_id,))
            
            versions = cursor.fetchall()
            conn.close()
            return versions
        except Exception as e:
            logger.error(f"获取脚本版本失败: {str(e)}")
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
