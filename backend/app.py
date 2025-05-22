# -*- coding: utf-8 -*-
"""
应用程序入口
初始化Flask应用并启动服务
"""
import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import config, logger
from models import initialize_db
from routes import script_bp, execution_bp, chain_bp, schedule_bp, alert_bp
from services import scheduler

def create_app(config_name='default'):
    """创建Flask应用"""
    # 创建应用实例
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 启用跨域
    CORS(app)
    
    # 初始化数据库
    initialize_db()
    
    # 启动定时任务调度服务
    scheduler.start()
    
    # 注册蓝图
    app.register_blueprint(script_bp)
    app.register_blueprint(execution_bp)
    app.register_blueprint(chain_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(alert_bp)
    
    # 前端路由
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file('index.html')
    
    # 创建脚本存储目录
    script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"启动应用服务，监听端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
