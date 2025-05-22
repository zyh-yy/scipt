# -*- coding: utf-8 -*-
"""
AI脚本生成相关路由
提供脚本生成、分析、验证等功能的API接口
"""
from flask import request, jsonify
from models.ai_generator import AIGenerator
from models.script import Script
from config import AI_API_KEY, logger

# 路由前缀会被自动添加为/api/scripts/ai

def generate_script():
    """生成脚本API"""
    try:
        # 获取请求参数
        data = request.get_json()
        
        # 必需的参数
        script_name = data.get('script_name')
        description = data.get('description')
        script_type = data.get('script_type')
        requirements = data.get('requirements')
        
        # 可选参数
        api_key = data.get('api_key', AI_API_KEY)
        model = data.get('model', 'qwen-plus')
        use_template = data.get('use_template', False)
        
        # 验证参数
        if not all([script_name, description, script_type, requirements]):
            return jsonify({
                'success': False,
                'error': '必需的参数不完整'
            }), 400
        
        # 脚本生成
        if use_template:
            # 使用模板生成
            template_language = data.get('template_language', 'python')
            template_has_params = data.get('template_has_params', True)
            template_output_mode = data.get('template_output_mode', 'json')
            
            success, script_content, error = AIGenerator.generate_script_from_template(
                template_language, template_has_params, template_output_mode,
                script_name, description, requirements, api_key, model
            )
        else:
            # 直接生成
            success, script_content, error = AIGenerator.generate_script(
                script_name, description, script_type, requirements, api_key, model
            )
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # 保存生成的脚本
        if data.get('save_script', True):
            url_path = data.get('url_path')
            save_success, script_id, file_path, save_error = AIGenerator.save_generated_script(
                script_name, description, script_type, script_content, url_path
            )
            
            if not save_success:
                return jsonify({
                    'success': False,
                    'error': save_error
                }), 500
            
            # 返回成功响应，包含脚本ID和内容
            return jsonify({
                'success': True,
                'script_id': script_id,
                'script_content': script_content,
                'file_path': file_path
            })
        else:
            # 不保存，仅返回生成的内容
            return jsonify({
                'success': True,
                'script_content': script_content
            })
            
    except Exception as e:
        logger.error(f"生成脚本API异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"生成脚本失败: {str(e)}"
        }), 500

def analyze_script(script_id):
    """分析脚本API"""
    try:
        # 获取请求参数
        analysis_type = request.args.get('type', 'general')
        
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'success': False,
                'error': f"脚本(ID:{script_id})不存在"
            }), 404
        
        # 分析脚本
        success, analysis_result, error = AIGenerator.analyze_script(
            script_id, analysis_type
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # 返回分析结果
        return jsonify({
            'success': True,
            'analysis_result': analysis_result
        })
        
    except Exception as e:
        logger.error(f"分析脚本API异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"分析脚本失败: {str(e)}"
        }), 500

def validate_script():
    """验证脚本API"""
    try:
        # 获取请求参数
        data = request.get_json()
        
        # 必需的参数
        script_content = data.get('script_content')
        script_type = data.get('script_type')
        requirements = data.get('requirements')
        
        # 可选参数
        api_key = data.get('api_key', AI_API_KEY)
        model = data.get('model', 'qwen-plus')
        
        # 验证参数
        if not all([script_content, script_type, requirements]):
            return jsonify({
                'success': False,
                'error': '必需的参数不完整'
            }), 400
        
        # 验证脚本
        success, validation_result, error = AIGenerator.validate_script(
            script_content, script_type, requirements, api_key, model
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # 返回验证结果
        return jsonify({
            'success': True,
            'validation_result': validation_result
        })
        
    except Exception as e:
        logger.error(f"验证脚本API异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"验证脚本失败: {str(e)}"
        }), 500




# 注册到routes/__init__.py时使用
def register_routes(bp):
    # 直接将路由添加到父蓝图
    bp.add_url_rule('/ai/generate', view_func=generate_script, methods=['POST'])
    bp.add_url_rule('/ai/analyze/<int:script_id>', view_func=analyze_script, methods=['GET'])
    bp.add_url_rule('/ai/validate', view_func=validate_script, methods=['POST'])
