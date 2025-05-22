# -*- coding: utf-8 -*-
"""
配置文件
包含应用程序配置和常量定义
"""
import os
import logging

# 基础配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'scripts.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'scripts')
ALLOWED_EXTENSIONS = {'py', 'sh', 'bat', 'ps1', 'js'}

# AI生成器配置
AI_API_KEY = "sk-5cdd3cf1d3a241898b4f82a26003f221"  # 替换为实际API密钥
AI_API_ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
SCRIPT_DIR = UPLOAD_FOLDER  # 脚本存储目录
DEFAULT_OUTPUT_MODE = "json"  # 默认输出模式

# 确保脚本存储目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'app.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 脚本执行配置
SCRIPT_TIMEOUT = 300  # 脚本执行超时时间（秒）
MAX_OUTPUT_SIZE = 1024 * 1024  # 最大输出大小（字节）

# Docker执行配置
USE_DOCKER = True  # 是否使用Docker容器执行脚本
DOCKER_TIMEOUT = 300  # Docker容器执行超时时间（秒）
DOCKER_DEFAULT_IMAGES = {
    'py': 'python:3.9-slim',
    'js': 'node:16-alpine',
    'sh': 'ubuntu:20.04',
    'bash': 'ubuntu:20.04',
    'ps1': 'mcr.microsoft.com/powershell:latest',
    'bat': 'mcr.microsoft.com/windows/servercore:ltsc2019'  # 注意：Windows容器需要Windows宿主机
}

# 应用配置
class Config:
    """应用基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    DEBUG = False
    
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
