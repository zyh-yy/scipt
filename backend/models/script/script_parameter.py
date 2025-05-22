# -*- coding: utf-8 -*-
"""
脚本参数模型
提供脚本参数的操作和管理，支持标准化的参数描述格式
"""
import os
import sys
import json
import datetime

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import logger

# 导入数据库管理器
from ..base import DBManager

class ScriptParameter:
    """脚本参数模型类"""
    
    @staticmethod
    def add(script_id, name, description, param_type, is_required=1, default_value=None, validation_rules=None):
        """添加脚本参数"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 如果提供了验证规则，将其转换为JSON字符串
            validation_json = None
            if validation_rules:
                validation_json = json.dumps(validation_rules, ensure_ascii=False)
            
            cursor.execute('''
            INSERT INTO script_parameters
            (script_id, name, description, param_type, is_required, default_value, validation_rules)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (script_id, name, description, param_type, is_required, default_value, validation_json))
            
            param_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加脚本参数成功: {name} 属于脚本ID {script_id}")
            return param_id
        except Exception as e:
            logger.error(f"添加脚本参数失败: {str(e)}")
            return None
    
    @staticmethod
    def update(param_id, name=None, description=None, param_type=None, is_required=None, 
               default_value=None, validation_rules=None):
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
            
            # 处理验证规则
            update_validation = None
            if validation_rules is not None:
                update_validation = json.dumps(validation_rules, ensure_ascii=False)
            else:
                update_validation = param.get('validation_rules')
            
            cursor.execute('''
            UPDATE script_parameters
            SET name = ?, description = ?, param_type = ?, is_required = ?, default_value = ?, validation_rules = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_type, update_required, update_default, update_validation, param_id))
            
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
            
            # 处理验证规则字段，将JSON字符串转换为字典
            for param in params:
                if param.get('validation_rules'):
                    try:
                        param['validation_rules'] = json.loads(param['validation_rules'])
                    except json.JSONDecodeError:
                        param['validation_rules'] = None
            
            conn.close()
            return params
        except Exception as e:
            logger.error(f"获取脚本参数失败: {str(e)}")
            return []
    
    @staticmethod
    def save_parameters_schema(script_id, schema):
        """保存脚本参数模式(schema)
        
        Args:
            script_id: 脚本ID
            schema: 参数模式，包含参数定义和验证规则的字典
        
        Returns:
            bool: 操作是否成功
        """
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 转换为JSON字符串
            schema_json = json.dumps(schema, ensure_ascii=False)
            
            # 检查记录是否存在
            cursor.execute("SELECT COUNT(*) as count FROM script_parameters_schema WHERE script_id = ?", (script_id,))
            result = cursor.fetchone()
            
            if result and result['count'] > 0:
                # 更新现有记录
                cursor.execute('''
                UPDATE script_parameters_schema
                SET schema = ?, updated_at = CURRENT_TIMESTAMP
                WHERE script_id = ?
                ''', (schema_json, script_id))
            else:
                # 插入新记录
                cursor.execute('''
                INSERT INTO script_parameters_schema
                (script_id, schema, created_at, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (script_id, schema_json))
            
            conn.commit()
            conn.close()
            
            logger.info(f"保存脚本参数模式成功: 脚本ID {script_id}")
            return True
        except Exception as e:
            logger.error(f"保存脚本参数模式失败: {str(e)}")
            return False
    
    @staticmethod
    def get_parameters_schema(script_id):
        """获取脚本参数模式(schema)
        
        Args:
            script_id: 脚本ID
        
        Returns:
            dict: 参数模式字典，如果没有则返回None
        """
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT schema FROM script_parameters_schema
            WHERE script_id = ?
            ''', (script_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result.get('schema'):
                try:
                    return json.loads(result['schema'])
                except json.JSONDecodeError:
                    logger.error(f"解析参数模式JSON失败: 脚本ID {script_id}")
                    return None
            else:
                return None
        except Exception as e:
            logger.error(f"获取脚本参数模式失败: {str(e)}")
            return None
    
    @staticmethod
    def create_default_schema(script_id):
        """为脚本创建默认参数模式
        
        Args:
            script_id: 脚本ID
        
        Returns:
            dict: 创建的参数模式字典
        """
        try:
            # 获取脚本的所有参数
            params = ScriptParameter.get_by_script(script_id)
            
            # 创建默认模式
            schema = {
                "parameters": []
            }
            
            # 添加参数定义
            for param in params:
                param_def = {
                    "name": param['name'],
                    "description": param['description'],
                    "type": param['param_type'],
                    "required": bool(param['is_required']),
                    "default": param['default_value']
                }
                
                # 添加验证规则（如果有）
                if param.get('validation_rules'):
                    param_def.update(param['validation_rules'])
                
                schema["parameters"].append(param_def)
            
            # 保存模式
            ScriptParameter.save_parameters_schema(script_id, schema)
            
            return schema
        except Exception as e:
            logger.error(f"创建默认参数模式失败: {str(e)}")
            return None
    
    @staticmethod
    def validate_parameters(script_id, params):
        """验证用户提供的参数是否符合模式要求
        
        Args:
            script_id: 脚本ID
            params: 用户提供的参数字典
        
        Returns:
            tuple: (验证是否通过, 错误信息)
        """
        try:
            # 获取参数模式
            schema = ScriptParameter.get_parameters_schema(script_id)
            
            # 如果没有模式，尝试创建默认模式
            if not schema:
                schema = ScriptParameter.create_default_schema(script_id)
                
            # 如果还是没有模式，无法验证
            if not schema or not schema.get('parameters'):
                return True, None
            
            # 验证参数
            missing_required = []
            type_errors = []
            validation_errors = []
            
            for param_def in schema['parameters']:
                name = param_def['name']
                is_required = param_def.get('required', False)
                
                # 检查必填参数
                if is_required and (name not in params or params[name] is None):
                    missing_required.append(name)
                    continue
                
                # 如果参数不存在，但不是必填，跳过
                if name not in params or params[name] is None:
                    continue
                
                # 获取参数值
                value = params[name]
                
                # 类型验证
                param_type = param_def.get('type', 'string')
                type_valid = True
                
                if param_type == 'string' and not isinstance(value, str):
                    type_valid = False
                elif param_type == 'integer' and not isinstance(value, int):
                    type_valid = False
                elif param_type == 'float' and not isinstance(value, (int, float)):
                    type_valid = False
                elif param_type == 'boolean' and not isinstance(value, bool):
                    type_valid = False
                elif param_type == 'array' and not isinstance(value, list):
                    type_valid = False
                elif param_type == 'object' and not isinstance(value, dict):
                    type_valid = False
                
                if not type_valid:
                    type_errors.append(f"{name} (预期类型: {param_type})")
                    continue
                
                # 验证规则检查
                if param_type in ('integer', 'float'):
                    # 数值范围检查
                    if 'min' in param_def and value < param_def['min']:
                        validation_errors.append(f"{name} 小于最小值 {param_def['min']}")
                    if 'max' in param_def and value > param_def['max']:
                        validation_errors.append(f"{name} 大于最大值 {param_def['max']}")
                
                elif param_type == 'string':
                    # 字符串模式匹配
                    if 'pattern' in param_def and re.search(param_def['pattern'], value) is None:
                        validation_errors.append(f"{name} 不匹配模式 {param_def['pattern']}")
                
                elif param_type == 'array':
                    # 数组长度检查
                    if 'min_items' in param_def and len(value) < param_def['min_items']:
                        validation_errors.append(f"{name} 元素数量少于 {param_def['min_items']}")
                    if 'max_items' in param_def and len(value) > param_def['max_items']:
                        validation_errors.append(f"{name} 元素数量超过 {param_def['max_items']}")
            
            # 汇总验证结果
            all_valid = (not missing_required and not type_errors and not validation_errors)
            
            error_msg = None
            if not all_valid:
                error_parts = []
                if missing_required:
                    error_parts.append(f"缺少必填参数: {', '.join(missing_required)}")
                if type_errors:
                    error_parts.append(f"参数类型错误: {', '.join(type_errors)}")
                if validation_errors:
                    error_parts.append(f"参数验证失败: {', '.join(validation_errors)}")
                error_msg = "; ".join(error_parts)
            
            return all_valid, error_msg
        except Exception as e:
            logger.error(f"验证参数失败: {str(e)}")
            return False, f"验证参数时发生错误: {str(e)}"
