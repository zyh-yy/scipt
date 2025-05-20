# -*- coding: utf-8 -*-
"""
脚本路由基础模块
提供通用函数和工具
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify
from . import script_bp
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, logger

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    """保存上传的文件并返回文件路径和类型"""
    # 检查文件名是否为空
    if file.filename == '':
        return None, None, '文件名不能为空'
    
    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        allowed_exts = ', '.join(ALLOWED_EXTENSIONS)
        return None, None, f'不支持的文件类型，只允许: {allowed_exts}'
    
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
    
    return file_path, file_type, None

def error_response(code, message, status_code=400):
    """返回错误响应"""
    return jsonify({
        'code': code,
        'message': message,
        'data': None
    }), status_code

def success_response(data=None, message='操作成功'):
    """返回成功响应"""
    return jsonify({
        'code': 0,
        'message': message,
        'data': data
    })
