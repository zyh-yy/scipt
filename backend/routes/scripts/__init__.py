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
from . import template
from . import ai_generator
from .version import version_list, version_edit, version_compare

# 注册AI脚本生成器路由
ai_generator.register_routes(script_bp)

# 导出Blueprint
__all__ = ['script_bp']
