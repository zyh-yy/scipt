# -*- coding: utf-8 -*-
"""
脚本基础CRUD操作
提供脚本的创建、读取、更新、删除功能
"""
import json
import os
from flask import request, jsonify
from . import script_bp
from .base import error_response, success_response
from models import Script, ScriptParameter
from config import logger

@script_bp.route('', methods=['GET'])
def get_scripts():
    """获取所有脚本列表"""
    try:
        scripts = Script.get_all()
        return success_response(scripts, '获取脚本列表成功')
    except Exception as e:
        logger.error(f"获取脚本列表失败: {str(e)}")
        return error_response(500, f'获取脚本列表失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """获取脚本详情"""
    try:
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        return success_response(script, '获取脚本详情成功')
    except Exception as e:
        logger.error(f"获取脚本详情失败: {str(e)}")
        return error_response(500, f'获取脚本详情失败: {str(e)}', 500)

@script_bp.route('', methods=['POST'])
def add_script():
    """添加新脚本"""
    try:
        # 获取表单或JSON数据
        if request.is_json:
            data = request.json
            name = data.get('name', '')
            description = data.get('description', '')
            file_path = data.get('file_path', '')
            file_type = data.get('file_type', '')
            params = data.get('parameters', [])
        else:
            name = request.form.get('name', '')
            description = request.form.get('description', '')
            file_path = request.form.get('file_path', '')
            file_type = request.form.get('file_type', '')
            params_json = request.form.get('parameters', '[]')
            try:
                params = json.loads(params_json)
            except:
                params = []
        
        # 验证必填字段
        if not name:
            return error_response(400, '脚本名称不能为空')
            
        if not file_path or not file_type:
            return error_response(400, '文件信息不完整')
            
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return error_response(400, '文件不存在')
        
        # 添加到数据库
        script_id = Script.add(name, description, file_path, file_type)
        
        if not script_id:
            # 删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            
            return error_response(500, '添加脚本到数据库失败', 500)
        
        # 处理参数信息
        if isinstance(params, list):
            for param in params:
                ScriptParameter.add(
                    script_id,
                    param.get('name'),
                    param.get('description', ''),
                    param.get('param_type', 'string'),
                    param.get('is_required', 1),
                    param.get('default_value')
                )
        
        # 获取完整的脚本信息
        script = Script.get(script_id)
        
        return success_response(script, '添加脚本成功')
    except Exception as e:
        logger.error(f"添加脚本失败: {str(e)}")
        return error_response(500, f'添加脚本失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>', methods=['PUT'])
def update_script(script_id):
    """更新脚本信息"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取更新数据
        data = request.json or {}
        name = data.get('name')
        description = data.get('description')
        
        # 更新脚本信息
        success = Script.update(script_id, name, description)
        
        if not success:
            return error_response(500, '更新脚本信息失败', 500)
        
        # 处理参数信息
        params = data.get('parameters')
        if params:
            # 先删除现有参数
            old_params = ScriptParameter.get_by_script(script_id)
            for old_param in old_params:
                ScriptParameter.delete(old_param['id'])
            
            # 添加新参数
            for param in params:
                ScriptParameter.add(
                    script_id,
                    param.get('name'),
                    param.get('description', ''),
                    param.get('param_type', 'string'),
                    param.get('is_required', 1),
                    param.get('default_value')
                )
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return success_response(updated_script, '更新脚本成功')
    except Exception as e:
        logger.error(f"更新脚本失败: {str(e)}")
        return error_response(500, f'更新脚本失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    """删除脚本"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # a 脚本
        success = Script.delete(script_id)
        
        if not success:
            return error_response(500, '删除脚本失败', 500)
        
        return success_response(None, '删除脚本成功')
    except Exception as e:
        logger.error(f"删除脚本失败: {str(e)}")
        return error_response(500, f'删除脚本失败: {str(e)}', 500)
