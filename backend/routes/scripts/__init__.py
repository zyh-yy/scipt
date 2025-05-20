# -*- coding: utf-8 -*-
"""
脚本管理相关路由
提供脚本上传、查询、修改、删除等接口
"""
from flask import Blueprint

script_bp = Blueprint('scripts', __name__, url_prefix='/api/scripts')

# 导入路由模块
from . import base
from . import crud
from . import upload
from .version import version_list, version_edit, version_compare

# 导出Blueprint
__all__ = ['script_bp']
