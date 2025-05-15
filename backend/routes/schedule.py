# -*- coding: utf-8 -*-
"""
定时任务相关路由
提供定时任务的创建、查询、修改和删除接口
"""
from flask import Blueprint, request, jsonify
from models import ScheduledTask
from services import scheduler
from config import logger

schedule_bp = Blueprint('schedule', __name__, url_prefix='/api/schedule')

@schedule_bp.route('', methods=['GET'])
def get_scheduled_tasks():
    """获取定时任务列表"""
    try:
        # 获取活动状态过滤参数
        is_active = request.args.get('is_active')
        if is_active is not None:
            is_active = int(is_active)
        
        # 获取定时任务列表
        tasks = ScheduledTask.get_all(is_active)
        
        return jsonify({
            'code': 0,
            'message': '获取定时任务列表成功',
            'data': tasks
        })
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取定时任务列表失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/<int:task_id>', methods=['GET'])
def get_scheduled_task(task_id):
    """获取定时任务详情"""
    try:
        # 获取定时任务详情
        task = ScheduledTask.get(task_id)
        
        if not task:
            return jsonify({
                'code': 404,
                'message': f'定时任务不存在: ID={task_id}',
                'data': None
            }), 404
        
        return jsonify({
            'code': 0,
            'message': '获取定时任务详情成功',
            'data': task
        })
    except Exception as e:
        logger.error(f"获取定时任务详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取定时任务详情失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('', methods=['POST'])
def add_scheduled_task():
    """添加定时任务"""
    try:
        data = request.json
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '定时任务名称不能为空',
                'data': None
            }), 400
        
        if not data.get('schedule_type'):
            return jsonify({
                'code': 400,
                'message': '调度类型不能为空',
                'data': None
            }), 400
        
        if not data.get('cron_expression'):
            return jsonify({
                'code': 400,
                'message': 'Cron表达式不能为空',
                'data': None
            }), 400
        
        # 检查脚本ID或脚本链ID必须指定一个
        if not data.get('script_id') and not data.get('chain_id'):
            return jsonify({
                'code': 400,
                'message': '必须指定脚本ID或脚本链ID',
                'data': None
            }), 400
        
        # 添加定时任务
        task_id = ScheduledTask.add(
            name=data.get('name'),
            description=data.get('description', ''),
            schedule_type=data.get('schedule_type'),
            cron_expression=data.get('cron_expression'),
            script_id=data.get('script_id'),
            chain_id=data.get('chain_id'),
            params=data.get('params')
        )
        
        if not task_id:
            return jsonify({
                'code': 500,
                'message': '添加定时任务失败',
                'data': None
            }), 500
        
        # 获取新添加的任务详情
        task = ScheduledTask.get(task_id)
        
        return jsonify({
            'code': 0,
            'message': '添加定时任务成功',
            'data': task
        })
    except Exception as e:
        logger.error(f"添加定时任务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'添加定时任务失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/<int:task_id>', methods=['PUT'])
def update_scheduled_task(task_id):
    """更新定时任务"""
    try:
        # 检查任务是否存在
        task = ScheduledTask.get(task_id)
        if not task:
            return jsonify({
                'code': 404,
                'message': f'定时任务不存在: ID={task_id}',
                'data': None
            }), 404
        
        data = request.json
        
        # 更新任务
        success = ScheduledTask.update(
            task_id=task_id,
            name=data.get('name'),
            description=data.get('description'),
            schedule_type=data.get('schedule_type'),
            cron_expression=data.get('cron_expression'),
            script_id=data.get('script_id'),
            chain_id=data.get('chain_id'),
            params=data.get('params'),
            is_active=data.get('is_active')
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新定时任务失败',
                'data': None
            }), 500
        
        # 获取更新后的任务详情
        updated_task = ScheduledTask.get(task_id)
        
        return jsonify({
            'code': 0,
            'message': '更新定时任务成功',
            'data': updated_task
        })
    except Exception as e:
        logger.error(f"更新定时任务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新定时任务失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/<int:task_id>/active', methods=['PUT'])
def toggle_task_active(task_id):
    """启用/禁用定时任务"""
    try:
        # 检查任务是否存在
        task = ScheduledTask.get(task_id)
        if not task:
            return jsonify({
                'code': 404,
                'message': f'定时任务不存在: ID={task_id}',
                'data': None
            }), 404
        
        data = request.json
        is_active = data.get('is_active', 1)
        
        # 更新任务活动状态
        success = ScheduledTask.update(
            task_id=task_id,
            is_active=is_active
        )
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新定时任务状态失败',
                'data': None
            }), 500
        
        status_text = "启用" if is_active else "禁用"
        
        return jsonify({
            'code': 0,
            'message': f'定时任务{status_text}成功',
            'data': {'id': task_id, 'is_active': is_active}
        })
    except Exception as e:
        logger.error(f"更新定时任务状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新定时任务状态失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_scheduled_task(task_id):
    """删除定时任务"""
    try:
        # 检查任务是否存在
        task = ScheduledTask.get(task_id)
        if not task:
            return jsonify({
                'code': 404,
                'message': f'定时任务不存在: ID={task_id}',
                'data': None
            }), 404
        
        # 删除任务
        success = ScheduledTask.delete(task_id)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '删除定时任务失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '删除定时任务成功',
            'data': None
        })
    except Exception as e:
        logger.error(f"删除定时任务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除定时任务失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/service/status', methods=['GET'])
def get_scheduler_status():
    """获取调度服务状态"""
    try:
        status = {
            'running': scheduler.running,
            'task_count': len(ScheduledTask.get_all(is_active=1)),
            'executor_count': len(scheduler.executors)
        }
        
        return jsonify({
            'code': 0,
            'message': '获取调度服务状态成功',
            'data': status
        })
    except Exception as e:
        logger.error(f"获取调度服务状态失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取调度服务状态失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/service/start', methods=['POST'])
def start_scheduler():
    """启动调度服务"""
    try:
        if scheduler.running:
            return jsonify({
                'code': 400,
                'message': '调度服务已经在运行中',
                'data': None
            }), 400
        
        success = scheduler.start()
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '启动调度服务失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '启动调度服务成功',
            'data': {'running': True}
        })
    except Exception as e:
        logger.error(f"启动调度服务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'启动调度服务失败: {str(e)}',
            'data': None
        }), 500

@schedule_bp.route('/service/stop', methods=['POST'])
def stop_scheduler():
    """停止调度服务"""
    try:
        if not scheduler.running:
            return jsonify({
                'code': 400,
                'message': '调度服务未运行',
                'data': None
            }), 400
        
        success = scheduler.stop()
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '停止调度服务失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '停止调度服务成功',
            'data': {'running': False}
        })
    except Exception as e:
        logger.error(f"停止调度服务失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'停止调度服务失败: {str(e)}',
            'data': None
        }), 500
