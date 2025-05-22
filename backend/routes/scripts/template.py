# -*- coding: utf-8 -*-
"""
脚本模板相关路由
提供脚本模板的获取功能
"""
from flask import request, jsonify
from . import script_bp
from .base import error_response, success_response
from config import logger
from utils.script_template_helper import ScriptTemplateHelper

@script_bp.route('/template', methods=['GET'])
def get_script_template():
    """获取脚本模板内容"""
    try:
        # 获取请求参数
        language = request.args.get('language', 'python')
        has_params = request.args.get('has_params', 'true').lower() == 'true'
        output_mode = request.args.get('output_mode', 'json')
        
        # 获取模板内容
        template_content = ScriptTemplateHelper.get_template_content(
            language=language,
            has_params=has_params,
            output_mode=output_mode
        )
        
        if template_content is None:
            return error_response(404, f'模板不存在: {language}, has_params={has_params}, output_mode={output_mode}')
        
        # 获取文件扩展名
        extension = ScriptTemplateHelper.get_extension(language)
        
        return success_response({
            'content': template_content,
            'language': language,
            'has_params': has_params,
            'output_mode': output_mode,
            'extension': extension
        })
    except Exception as e:
        logger.error(f"获取脚本模板失败: {str(e)}")
        return error_response(500, f'获取脚本模板失败: {str(e)}')

@script_bp.route('/template/languages', methods=['GET'])
def get_script_languages():
    """获取支持的脚本语言列表"""
    try:
        return success_response({
            'languages': list(ScriptTemplateHelper.LANGUAGES.keys()),
            'output_modes': ScriptTemplateHelper.OUTPUT_MODES
        })
    except Exception as e:
        logger.error(f"获取脚本语言列表失败: {str(e)}")
        return error_response(500, f'获取脚本语言列表失败: {str(e)}')
