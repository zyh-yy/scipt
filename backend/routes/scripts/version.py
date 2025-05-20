# -*- coding: utf-8 -*-
"""
脚本版本控制相关路由
提供脚本版本历史、版本回滚和版本比较功能
"""
import os
import hashlib
import difflib
from datetime import datetime
from flask import request
from . import script_bp
from .base import error_response, success_response, save_uploaded_file
from models import Script, ScriptVersion
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

@script_bp.route('/<int:script_id>/versions/<int:version_id>/content', methods=['GET'])
def get_version_content(script_id, version_id):
    """获取指定版本的文件内容"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取版本信息
        versions = ScriptVersion.get_versions(script_id)
        version = next((v for v in versions if v['id'] == version_id), None)
        
        if not version:
            return error_response(404, f'版本不存在: ID={version_id}', 404)
        
        # 获取文件内容
        try:
            with open(version['file_path'], 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"读取脚本文件失败: {str(e)}")
            return error_response(500, f'读取脚本文件失败: {str(e)}', 500)
        
        return success_response({
            'version': version,
            'content': content
        }, '获取脚本版本内容成功')
    except Exception as e:
        logger.error(f"获取脚本版本内容失败: {str(e)}")
        return error_response(500, f'获取脚本版本内容失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>/versions/compare', methods=['GET'])
def compare_script_versions(script_id):
    """比较两个版本的差异"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取要比较的版本ID
        version_id1 = int(request.args.get('version_id1', 0))
        version_id2 = int(request.args.get('version_id2', 0))
        
        if not version_id1 or not version_id2:
            return error_response(400, '请提供两个版本ID进行比较')
        
        # 获取版本信息
        versions = ScriptVersion.get_versions(script_id)
        version1 = next((v for v in versions if v['id'] == version_id1), None)
        version2 = next((v for v in versions if v['id'] == version_id2), None)
        
        if not version1 or not version2:
            return error_response(404, '指定的版本不存在', 404)
        
        # 读取文件内容
        try:
            with open(version1['file_path'], 'r', encoding='utf-8') as f:
                content1 = f.read().splitlines()
            
            with open(version2['file_path'], 'r', encoding='utf-8') as f:
                content2 = f.read().splitlines()
        except Exception as e:
            logger.error(f"读取脚本文件失败: {str(e)}")
            return error_response(500, f'读取脚本文件失败: {str(e)}', 500)
        
        # 生成diff
        diff = difflib.unified_diff(
            content1,
            content2,
            fromfile=f"版本 {version1['version']}",
            tofile=f"版本 {version2['version']}",
            lineterm=''
        )
        
        # 转换为HTML格式的差异
        diff_text = '\n'.join(diff)
        
        return success_response({
            'version1': version1,
            'version2': version2,
            'diff': diff_text
        }, '比较脚本版本成功')
    except Exception as e:
        logger.error(f"比较脚本版本失败: {str(e)}")
        return error_response(500, f'比较脚本版本失败: {str(e)}', 500)
