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
