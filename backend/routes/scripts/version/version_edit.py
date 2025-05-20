# -*- coding: utf-8 -*-
"""
脚本版本创建和回滚路由
提供脚本版本创建和回滚功能
"""
import os
from flask import request
from .. import script_bp
from ..base import error_response, success_response, save_uploaded_file
from models.script import Script, ScriptVersion
from config import logger

@script_bp.route('/<int:script_id>/versions', methods=['POST'])
def create_script_version(script_id):
    """创建脚本新版本"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取版本信息
        version = request.form.get('version')
        description = request.form.get('description', '')
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response(400, '请选择脚本文件')
        
        file = request.files['file']
        
        # 保存文件
        file_path, file_type, error_msg = save_uploaded_file(file)
        if error_msg:
            return error_response(400, error_msg)
        
        # 添加版本
        version_id = ScriptVersion.add(
            script_id, 
            file_path, 
            version=version, 
            description=description
        )
        
        if not version_id:
            # 删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            
            return error_response(500, '创建脚本版本失败', 500)
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return success_response(updated_script, '创建脚本版本成功')
    except Exception as e:
        logger.error(f"创建脚本版本失败: {str(e)}")
        return error_response(500, f'创建脚本版本失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>/versions/<int:version_id>/rollback', methods=['PUT'])
def rollback_script_version(script_id, version_id):
    """回滚到指定版本"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 检查版本是否存在
        version = ScriptVersion.get_version_by_id(version_id)
        if not version or version['script_id'] != script_id:
            return error_response(404, f'版本不存在: ID={version_id}', 404)
        
        # 回滚到指定版本
        success = Script.set_version_current(script_id, version_id)
        
        if not success:
            return error_response(500, '回滚脚本版本失败', 500)
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return success_response(updated_script, '回滚脚本版本成功')
    except Exception as e:
        logger.error(f"回滚脚本版本失败: {str(e)}")
        return error_response(500, f'回滚脚本版本失败: {str(e)}', 500)
