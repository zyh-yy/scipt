# -*- coding: utf-8 -*-
"""
脚本文件上传相关路由
提供脚本文件的上传和更新功能
"""
import json
import os
from flask import request
from . import script_bp
from .base import error_response, success_response, save_uploaded_file
from models import Script, ScriptParameter
from config import logger

@script_bp.route('/with-file', methods=['POST'])
def add_script_with_file():
    """添加新脚本（同时上传文件）"""
    try:
        # 获取表单数据
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        params_json = request.form.get('parameters', '[]')
        
        # 验证必填字段
        if not name:
            return error_response(400, '脚本名称不能为空')
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response(400, '请选择脚本文件')
        
        file = request.files['file']
        
        # 保存文件
        file_path, file_type, error_msg = save_uploaded_file(file)
        if error_msg:
            return error_response(400, error_msg)
        
        # 解析参数数据
        try:
            params = json.loads(params_json)
        except:
            params = []
        
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
        
@script_bp.route('/upload-file', methods=['POST'])
def upload_script_file():
    """上传脚本文件，返回文件ID"""
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response(400, '请选择要上传的脚本文件')
        
        file = request.files['file']
        
        # 保存文件
        file_path, file_type, error_msg = save_uploaded_file(file)
        if error_msg:
            return error_response(400, error_msg)
        
        # 返回文件信息
        return success_response({
            'file_path': file_path,
            'file_type': file_type,
            'original_name': file.filename
        }, '文件上传成功')
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        return error_response(500, f'上传文件失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>/file', methods=['PUT'])
def update_script_file(script_id):
    """更新脚本文件"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response(400, '请选择要上传的脚本文件')
        
        file = request.files['file']
        
        # 保存文件
        file_path, file_type, error_msg = save_uploaded_file(file)
        if error_msg:
            return error_response(400, error_msg)
        
        # 删除旧文件
        old_file_path = script['file_path']
        try:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        except Exception as e:
            logger.warning(f"删除旧文件失败: {str(e)}")
        
        # 更新数据库记录
        success = Script.update(script_id, file_path=file_path, file_type=file_type)
        
        if not success:
            # 删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            
            return error_response(500, '更新脚本文件失败', 500)
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return success_response(updated_script, '更新脚本文件成功')
    except Exception as e:
        logger.error(f"更新脚本文件失败: {str(e)}")
        return error_response(500, f'更新脚本文件失败: {str(e)}', 500)
