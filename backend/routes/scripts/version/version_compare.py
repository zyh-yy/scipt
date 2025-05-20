# -*- coding: utf-8 -*-
"""
脚本版本比较路由
提供脚本版本比较功能
"""
import difflib
from flask import request
from .. import script_bp
from ..base import error_response, success_response
from models.script import Script, ScriptVersion
from config import logger

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
        version1 = ScriptVersion.get_version_by_id(version_id1)
        version2 = ScriptVersion.get_version_by_id(version_id2)
        
        if not version1 or not version2:
            return error_response(404, '指定的版本不存在', 404)
        
        if version1['script_id'] != script_id or version2['script_id'] != script_id:
            return error_response(400, '指定的版本不属于该脚本', 400)
        
        # 使用ScriptVersion类提供的比较功能
        diff_text = ScriptVersion.compare_versions(version_id1, version_id2)
        
        if diff_text is None:
            return error_response(500, '比较脚本版本失败', 500)
        
        # 返回比较结果
        return success_response({
            'version1': version1,
            'version2': version2,
            'diff': diff_text
        }, '比较脚本版本成功')
    except Exception as e:
        logger.error(f"比较脚本版本失败: {str(e)}")
        return error_response(500, f'比较脚本版本失败: {str(e)}', 500)

@script_bp.route('/<int:script_id>/versions/compare/html', methods=['GET'])
def compare_script_versions_html(script_id):
    """比较两个版本的差异，返回HTML格式结果"""
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
        version1 = ScriptVersion.get_version_by_id(version_id1)
        version2 = ScriptVersion.get_version_by_id(version_id2)
        
        if not version1 or not version2:
            return error_response(404, '指定的版本不存在', 404)
        
        if version1['script_id'] != script_id or version2['script_id'] != script_id:
            return error_response(400, '指定的版本不属于该脚本', 400)
        
        # 获取文件内容
        content1 = ScriptVersion.get_file_content(version_id1)
        content2 = ScriptVersion.get_file_content(version_id2)
        
        if content1 is None or content2 is None:
            return error_response(500, '读取脚本文件失败', 500)
        
        # 生成HTML格式的差异
        diff = difflib.HtmlDiff()
        diff_html = diff.make_file(
            content1.splitlines(),
            content2.splitlines(),
            f"版本 {version1['version']}",
            f"版本 {version2['version']}",
            context=True,
            numlines=3
        )
        
        return success_response({
            'version1': version1,
            'version2': version2,
            'diff_html': diff_html
        }, '比较脚本版本成功')
    except Exception as e:
        logger.error(f"比较脚本版本失败: {str(e)}")
        return error_response(500, f'比较脚本版本失败: {str(e)}', 500)
