# -*- coding: utf-8 -*-
"""
脚本管理相关路由
提供脚本上传、查询、修改、删除等接口
"""
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import Script, ScriptParameter
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, logger

script_bp = Blueprint('scripts', __name__, url_prefix='/api/scripts')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@script_bp.route('', methods=['GET'])
def get_scripts():
    """获取所有脚本列表"""
    try:
        scripts = Script.get_all()
        return jsonify({
            'code': 0,
            'message': '获取脚本列表成功',
            'data': scripts
        })
    except Exception as e:
        logger.error(f"获取脚本列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取脚本列表失败: {str(e)}',
            'data': None
        }), 500

@script_bp.route('/<int:script_id>', methods=['GET'])
def get_script(script_id):
    """获取脚本详情"""
    try:
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'code': 404,
                'message': f'脚本不存在: ID={script_id}',
                'data': None
            }), 404
        
        return jsonify({
            'code': 0,
            'message': '获取脚本详情成功',
            'data': script
        })
    except Exception as e:
        logger.error(f"获取脚本详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取脚本详情失败: {str(e)}',
            'data': None
        }), 500

@script_bp.route('/upload-file', methods=['POST'])
def upload_script_file():
    """上传脚本文件，返回文件ID"""
    try:
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '请选择要上传的脚本文件',
                'data': None
            }), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '文件名不能为空',
                'data': None
            }), 400
        
        # 检查文件类型是否允许
        if not allowed_file(file.filename):
            allowed_exts = ', '.join(ALLOWED_EXTENSIONS)
            return jsonify({
                'code': 400,
                'message': f'不支持的文件类型，只允许: {allowed_exts}',
                'data': None
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"  # 添加时间戳防止文件名冲突
        
        # 确保上传目录存在
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # 获取文件类型
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # 返回文件信息
        return jsonify({
            'code': 0,
            'message': '文件上传成功',
            'data': {
                'file_path': file_path,
                'file_type': file_type,
                'original_name': file.filename
            }
        })
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'上传文件失败: {str(e)}',
            'data': None
        }), 500

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
            return jsonify({
                'code': 400,
                'message': '脚本名称不能为空',
                'data': None
            }), 400
            
        if not file_path or not file_type:
            return jsonify({
                'code': 400,
                'message': '文件信息不完整',
                'data': None
            }), 400
            
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return jsonify({
                'code': 400,
                'message': '文件不存在',
                'data': None
            }), 400
        
        # 添加到数据库
        script_id = Script.add(name, description, file_path, file_type)
        
        if not script_id:
            # 删除已上传的文件
            try:
                os.remove(file_path)
            except:
                pass
            
            return jsonify({
                'code': 500,
                'message': '添加脚本到数据库失败',
                'data': None
            }), 500
        
        # 处理参数信息
        params_json = request.form.get('parameters')
        if params_json:
            try:
                params = json.loads(params_json)
                for param in params:
                    ScriptParameter.add(
                        script_id,
                        param.get('name'),
                        param.get('description', ''),
                        param.get('param_type', 'string'),
                        param.get('is_required', 1),
                        param.get('default_value')
                    )
            except Exception as e:
                logger.error(f"添加脚本参数失败: {str(e)}")
        
        # 获取完整的脚本信息
        script = Script.get(script_id)
        
        return jsonify({
            'code': 0,
            'message': '添加脚本成功',
            'data': script
        })
    except Exception as e:
        logger.error(f"添加脚本失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加脚本失败: {str(e)}',
            'data': None
        }), 500

@script_bp.route('/<int:script_id>', methods=['PUT'])
def update_script(script_id):
    """更新脚本信息"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'code': 404,
                'message': f'脚本不存在: ID={script_id}',
                'data': None
            }), 404
        
        # 获取更新数据
        data = request.json or {}
        name = data.get('name')
        description = data.get('description')
        
        # 更新脚本信息
        success = Script.update(script_id, name, description)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新脚本信息失败',
                'data': None
            }), 500
        
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
        
        return jsonify({
            'code': 0,
            'message': '更新脚本成功',
            'data': updated_script
        })
    except Exception as e:
        logger.error(f"更新脚本失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新脚本失败: {str(e)}',
            'data': None
        }), 500

@script_bp.route('/<int:script_id>/file', methods=['PUT'])
def update_script_file(script_id):
    """更新脚本文件"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'code': 404,
                'message': f'脚本不存在: ID={script_id}',
                'data': None
            }), 404
        
        # 检查文件是否存在
        if 'file' not in request.files:
            return jsonify({
                'code': 400,
                'message': '请选择要上传的脚本文件',
                'data': None
            }), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'code': 400,
                'message': '文件名不能为空',
                'data': None
            }), 400
        
        # 检查文件类型是否允许
        if not allowed_file(file.filename):
            allowed_exts = ', '.join(ALLOWED_EXTENSIONS)
            return jsonify({
                'code': 400,
                'message': f'不支持的文件类型，只允许: {allowed_exts}',
                'data': None
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"  # 添加时间戳防止文件名冲突
        
        # 确保上传目录存在
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # 获取文件类型
        file_type = filename.rsplit('.', 1)[1].lower()
        
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
            
            return jsonify({
                'code': 500,
                'message': '更新脚本文件失败',
                'data': None
            }), 500
        
        # 获取更新后的脚本信息
        updated_script = Script.get(script_id)
        
        return jsonify({
            'code': 0,
            'message': '更新脚本文件成功',
            'data': updated_script
        })
    except Exception as e:
        logger.error(f"更新脚本文件失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新脚本文件失败: {str(e)}',
            'data': None
        }), 500

@script_bp.route('/<int:script_id>', methods=['DELETE'])
def delete_script(script_id):
    """删除脚本"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'code': 404,
                'message': f'脚本不存在: ID={script_id}',
                'data': None
            }), 404
        
        # 软删除脚本
        success = Script.delete(script_id)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '删除脚本失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '删除脚本成功',
            'data': None
        })
    except Exception as e:
        logger.error(f"删除脚本失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除脚本失败: {str(e)}',
            'data': None
        }), 500
