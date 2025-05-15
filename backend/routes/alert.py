# -*- coding: utf-8 -*-
"""
告警相关路由
提供告警配置和历史查询接口
"""
from flask import Blueprint, request, jsonify
from models import AlertConfig, AlertHistory
from services import EmailService
from config import logger


alert_bp = Blueprint('alert', __name__, url_prefix='/api/alert')

@alert_bp.route('/config', methods=['GET'])
def get_alert_configs():
    """获取告警配置列表"""
    try:
        # 获取活动状态过滤参数
        is_active = request.args.get('is_active')
        if is_active is not None:
            is_active = int(is_active)
        
        # 获取告警配置列表
        configs = AlertConfig.get_all(is_active)
        
        return jsonify({
            'code': 0,
            'message': '获取告警配置列表成功',
            'data': configs
        })
    except Exception as e:
        logger.error(f"获取告警配置列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取告警配置列表失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/config/<int:config_id>', methods=['GET'])
def get_alert_config(config_id):
    """获取告警配置详情"""
    try:
        # 获取告警配置详情
        config = AlertConfig.get(config_id)
        
        if not config:
            return jsonify({
                'code': 404,
                'message': f'告警配置不存在: ID={config_id}',
                'data': None
            }), 404
        
        return jsonify({
            'code': 0,
            'message': '获取告警配置详情成功',
            'data': config
        })
    except Exception as e:
        logger.error(f"获取告警配置详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取告警配置详情失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/config', methods=['POST'])
def add_alert_config():
    """添加告警配置"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '告警名称不能为空',
                'data': None
            }), 400
        
        if not data.get('alert_type'):
            return jsonify({
                'code': 400,
                'message': '告警类型不能为空',
                'data': None
            }), 400
        
        if not data.get('condition_type') or not data.get('condition_value'):
            return jsonify({
                'code': 400,
                'message': '告警条件不能为空',
                'data': None
            }), 400
        
        if not data.get('notification_type') or not data.get('notification_config'):
            return jsonify({
                'code': 400,
                'message': '通知配置不能为空',
                'data': None
            }), 400
        
        # 添加告警配置
        config_id = AlertConfig.add(
            name=data.get('name'),
            description=data.get('description', ''),
            alert_type=data.get('alert_type'),
            condition_type=data.get('condition_type'),
            condition_value=data.get('condition_value'),
            notification_type=data.get('notification_type'),
            notification_config=data.get('notification_config')
        )
        
        if not config_id:
            return jsonify({
                'code': 500,
                'message': '添加告警配置失败',
                'data': None
            }), 500
        
        # 获取新添加的配置详情
        config = AlertConfig.get(config_id)
        
        return jsonify({
            'code': 0,
            'message': '添加告警配置成功',
            'data': config
        })
    except Exception as e:
        logger.error(f"添加告警配置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加告警配置失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/config/<int:config_id>', methods=['PUT'])
def update_alert_config(config_id):
    """更新告警配置"""
    try:
        # 检查配置是否存在
        config = AlertConfig.get(config_id)
        if not config:
            return jsonify({
                'code': 404,
                'message': f'告警配置不存在: ID={config_id}',
                'data': None
            }), 404
        
        data = request.json
        
        # 更新配置
        success = AlertConfig.update(
            config_id=config_id,
            name=data.get('name'),
            description=data.get('description'),
            alert_type=data.get('alert_type'),
            condition_type=data.get('condition_type'),
            condition_value=data.get('condition_value'),
            notification_type=data.get('notification_type'),
            notification_config=data.get('notification_config'),
            is_active=data.get('is_active')
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新告警配置失败',
                'data': None
            }), 500
        
        # 获取更新后的配置详情
        updated_config = AlertConfig.get(config_id)
        
        return jsonify({
            'code': 0,
            'message': '更新告警配置成功',
            'data': updated_config
        })
    except Exception as e:
        logger.error(f"更新告警配置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新告警配置失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/config/<int:config_id>/active', methods=['PUT'])
def toggle_config_active(config_id):
    """启用/禁用告警配置"""
    try:
        # 检查配置是否存在
        config = AlertConfig.get(config_id)
        if not config:
            return jsonify({
                'code': 404,
                'message': f'告警配置不存在: ID={config_id}',
                'data': None
            }), 404
        
        data = request.json
        is_active = data.get('is_active', 1)
        
        # 更新配置活动状态
        success = AlertConfig.update(
            config_id=config_id,
            is_active=is_active
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新告警配置状态失败',
                'data': None
            }), 500
        
        status_text = "启用" if is_active else "禁用"
        
        return jsonify({
            'code': 0,
            'message': f'告警配置{status_text}成功',
            'data': {'id': config_id, 'is_active': is_active}
        })
    except Exception as e:
        logger.error(f"更新告警配置状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新告警配置状态失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/config/<int:config_id>', methods=['DELETE'])
def delete_alert_config(config_id):
    """删除告警配置"""
    try:
        # 检查配置是否存在
        config = AlertConfig.get(config_id)
        if not config:
            return jsonify({
                'code': 404,
                'message': f'告警配置不存在: ID={config_id}',
                'data': None
            }), 404
        
        # 删除配置
        success = AlertConfig.delete(config_id)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '删除告警配置失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '删除告警配置成功',
            'data': None
        })
    except Exception as e:
        logger.error(f"删除告警配置失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除告警配置失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/history', methods=['GET'])
def get_alert_histories():
    """获取告警历史列表"""
    try:
        # 获取分页参数
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        config_id = request.args.get('config_id')
        
        if config_id:
            config_id = int(config_id)
        
        # 获取告警历史列表
        histories = AlertHistory.get_all(limit, offset, config_id)
        
        return jsonify({
            'code': 0,
            'message': '获取告警历史列表成功',
            'data': histories
        })
    except Exception as e:
        logger.error(f"获取告警历史列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取告警历史列表失败: {str(e)}',
            'data': None
        }), 500

@alert_bp.route('/test-email', methods=['POST'])
def test_email():
    """测试邮件发送"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('smtp_server') or not data.get('smtp_port'):
            return jsonify({
                'code': 400,
                'message': 'SMTP服务器信息不完整',
                'data': None
            }), 400
        
        if not data.get('username') or not data.get('password'):
            return jsonify({
                'code': 400,
                'message': 'SMTP账号信息不完整',
                'data': None
            }), 400
        
        if not data.get('sender') or not data.get('recipients'):
            return jsonify({
                'code': 400,
                'message': '发件人或收件人不能为空',
                'data': None
            }), 400
        
        # 先测试连接
        smtp_server = data.get('smtp_server')
        smtp_port = int(data.get('smtp_port'))
        username = data.get('username')
        password = data.get('password')
        
        success, message = EmailService.test_connection(
            smtp_server, smtp_port, username, password
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': message,
                'data': None
            }), 500
        
        # 发送测试邮件
        email_service = EmailService(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            username=username,
            password=password,
            default_sender=data.get('sender')
        )
        
        success = email_service.send_email(
            recipients=data.get('recipients'),
            subject="脚本管理平台 - 测试邮件",
            body="这是一封来自脚本管理平台的测试邮件，如果您收到此邮件，说明邮件服务配置正确。",
            html=True
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '测试邮件发送失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '测试邮件发送成功',
            'data': None
        })
    except Exception as e:
        logger.error(f"测试邮件发送失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'测试邮件发送失败: {str(e)}',
            'data': None
        }), 500
