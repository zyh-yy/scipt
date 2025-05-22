# -*- coding: utf-8 -*-
"""
脚本内容编辑路由
提供脚本内容和参数的更新功能
"""
import os
import tempfile
from flask import request
from .. import script_bp
from ..base import error_response, success_response, save_uploaded_file
from models.script import Script, ScriptVersion
from config import logger

@script_bp.route('/<int:script_id>/content', methods=['POST'])
def update_script_content(script_id):
    """更新脚本内容和参数"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return error_response(404, f'脚本不存在: ID={script_id}', 404)
        
        # 获取版本描述
        description = request.form.get('description', '脚本内容编辑')
        
        # 获取更新后的参数
        try:
            import json
            parameters_json = request.form.get('parameters', '[]')
            parameters = json.loads(parameters_json)
        except Exception as e:
            return error_response(400, f'参数格式错误: {str(e)}')
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return error_response(400, '请提供脚本内容文件')
        
        file = request.files['file']
        
        # 保存文件
        file_path, file_type, error_msg = save_uploaded_file(file)
        if error_msg:
            return error_response(400, error_msg)
        
        # 如果未指定文件类型，使用原始脚本类型
        if not file_type and script.get('file_type'):
            file_type = script.get('file_type')
            
            # 如果保存的文件没有正确的扩展名，重命名它
            if not file_path.endswith(f'.{file_type}'):
                new_file_path = f"{file_path}.{file_type}"
                try:
                    os.rename(file_path, new_file_path)
                    file_path = new_file_path
                except Exception as e:
                    logger.error(f"重命名文件失败: {str(e)}")
        
        # 添加版本
        version_id = ScriptVersion.add(
            script_id, 
            file_path, 
            description=description
        )
        
        if not version_id:
            # 删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            
            return error_response(500, '更新脚本内容失败', 500)
        
        # 更新脚本参数
        success = Script.update_parameters(script_id, parameters)
        if not success:
            return error_response(500, '更新脚本参数失败', 500)
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return success_response(updated_script, '更新脚本内容成功')
    except Exception as e:
        logger.error(f"更新脚本内容失败: {str(e)}")
        return error_response(500, f'更新脚本内容失败: {str(e)}', 500)
