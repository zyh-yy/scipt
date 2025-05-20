# -*- coding: utf-8 -*-
"""
脚本版本列表和内容获取路由
提供脚本版本历史和版本内容查询功能
"""
from flask import request
from .. import script_bp
from ..base import error_response, success_response
from models.script import Script, ScriptVersion
from config import logger

@script_bp.route('/<int:script_id>/versions', methods=['GET'])
def get_script_versions(script_id):
    """获取脚本的版本历史"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取版本历史
        versions = ScriptVersion.get_versions(script_id)
        
        return success_response(versions, '获取脚本版本历史成功')
    except Exception as e:
        logger.error(f"获取脚本版本历史失败: {str(e)}")
        return error_response(500, f'获取脚本版本历史失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>/versions/<int:version_id>/content', methods=['GET'])
def get_version_content(script_id, version_id):
    """获取指定版本的文件内容"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取版本信息
        version = ScriptVersion.get_version_by_id(version_id)
        if not version or version['script_id'] != script_id:
            return error_response(404, f'版本不存在: ID={version_id}', 404)
        
        # 获取文件内容
        content = ScriptVersion.get_file_content(version_id)
        if content is None:
            return error_response(500, '读取脚本文件失败', 500)
        
        return success_response({
            'version': version,
            'content': content
        }, '获取脚本版本内容成功')
    except Exception as e:
        logger.error(f"获取脚本版本内容失败: {str(e)}")
        return error_response(500, f'获取脚本版本内容失败: {str(e)}', 500)
