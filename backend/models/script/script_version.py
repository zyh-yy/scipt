# -*- coding: utf-8 -*-
"""
脚本版本模型
提供脚本版本的操作和管理
"""
import os
import sys
import datetime
import hashlib
import sqlite3

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import logger

# 导入数据库管理器
from ..base import DBManager

class ScriptVersion:
    """脚本版本模型类"""
    
    @staticmethod
    def add(script_id, file_path, version=None, description=None, force_create=False):
        """添加脚本版本
        
        Args:
            script_id: 脚本ID
            file_path: 文件路径
            version: 版本号，如果为None则自动生成
            description: 版本描述
            force_create: 是否强制创建新版本，即使内容与最新版本相同
            
        Returns:
            int: 版本ID，如果失败则返回None
        """
        try:
            # 计算文件内容的哈希值
            content_hash = ScriptVersion._calculate_file_hash(file_path)
            if not content_hash:
                logger.error("计算文件哈希值失败")
                return None
                
            # 检查是否与最新版本内容相同
            latest_version = ScriptVersion.get_latest_version(script_id)
            if not force_create and latest_version and latest_version.get('content_hash') == content_hash:
                logger.info(f"脚本内容未变化，不创建新版本: 脚本ID {script_id}")
                return latest_version['id']
            
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            # 获取最新版本号并计算新版本号
            if not version:
                version = ScriptVersion._generate_next_version(script_id)
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 将所有现有版本设为非当前版本
            cursor.execute('''
            UPDATE script_versions SET is_current = 0 WHERE script_id = ?
            ''', (script_id,))
            
            # 添加新版本
            cursor.execute('''
            INSERT INTO script_versions 
            (script_id, version, file_path, is_current, description, created_at, content_hash)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            ''', (script_id, version, file_path, description, now, content_hash))
            
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
    def _calculate_file_hash(file_path):
        """计算文件内容的SHA-256哈希值"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None
                
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"计算文件哈希值失败: {str(e)}")
            return None
            
    @staticmethod
    def _generate_next_version(script_id):
        """生成下一个版本号"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT version FROM script_versions 
            WHERE script_id = ? ORDER BY id DESC LIMIT 1
            ''', (script_id,))
            latest_version = cursor.fetchone()
            conn.close()
            
            if latest_version:
                version_parts = latest_version['version'].split('.')
                # 增加最后一位
                new_version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
            else:
                new_version = "1.0.0"
                
            return new_version
        except Exception as e:
            logger.error(f"生成版本号失败: {str(e)}")
            return "1.0.0"  # 默认返回1.0.0
        
    @staticmethod
    def get_latest_version(script_id):
        """获取脚本的最新版本"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_versions
            WHERE script_id = ?
            ORDER BY id DESC LIMIT 1
            ''', (script_id,))
            
            version = cursor.fetchone()
            conn.close()
            return version
        except Exception as e:
            logger.error(f"获取脚本最新版本失败: {str(e)}")
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
    
    @staticmethod
    def get_version_by_id(version_id):
        """根据ID获取版本信息"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM script_versions
            WHERE id = ?
            ''', (version_id,))
            
            version = cursor.fetchone()
            conn.close()
            return version
        except Exception as e:
            logger.error(f"获取脚本版本失败: {str(e)}")
            return None
    
    @staticmethod
    def get_file_content(version_id):
        """获取指定版本的文件内容"""
        try:
            version = ScriptVersion.get_version_by_id(version_id)
            if not version:
                return None
                
            # 优先从数据库中读取内容
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT content FROM script_versions WHERE id = ?", (version_id,))
                result = cursor.fetchone()
                if result and result['content']:
                    logger.info(f"从数据库中读取脚本内容成功: 版本ID {version_id}")
                    conn.close()
                    return result['content']
            except sqlite3.OperationalError as e:
                # 如果没有content列，则忽略错误
                pass
            
            conn.close()
                
            # 如果数据库中没有内容，则尝试从文件中读取
            if not version['file_path']:
                return None
                
            # 读取文件内容
            try:
                with open(version['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"从文件中读取脚本内容成功: {version['file_path']}")
                return content
            except Exception as e:
                logger.error(f"读取脚本文件失败: {str(e)}")
                
                # 如果指定文件读取失败，尝试从脚本原始文件读取
                # 避免循环导入
                script = None
                conn = DBManager.get_connection()
                conn.row_factory = DBManager.dict_factory
                cursor = conn.cursor()
                
                cursor.execute('''
                SELECT * FROM scripts WHERE id = ?
                ''', (version['script_id'],))
                
                script = cursor.fetchone()
                conn.close()
                if script and script['file_path'] and os.path.exists(script['file_path']):
                    try:
                        with open(script['file_path'], 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        logger.info(f"从原始脚本文件中读取内容成功: {script['file_path']}")
                        return content
                    except Exception as e2:
                        logger.error(f"读取原始脚本文件失败: {str(e2)}")
                
                return None
        except Exception as e:
            logger.error(f"获取脚本版本文件内容失败: {str(e)}")
            return None
    
    @staticmethod
    def compare_versions(version_id1, version_id2):
        """比较两个版本的差异"""
        try:
            import difflib
            
            content1 = ScriptVersion.get_file_content(version_id1)
            content2 = ScriptVersion.get_file_content(version_id2)
            
            if content1 is None or content2 is None:
                return None
                
            # 使用difflib生成差异
            diff = difflib.unified_diff(
                content1.splitlines(True),
                content2.splitlines(True),
                'Version 1',
                'Version 2'
            )
            
            return ''.join(diff)
        except Exception as e:
            logger.error(f"比较脚本版本失败: {str(e)}")
            return None
