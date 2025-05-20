# -*- coding: utf-8 -*-
"""
脚本执行相关路由
提供脚本执行、查询执行历史等接口
"""
import os
import json
from flask import Blueprint, request, jsonify, current_app
from models import Script, ScriptParameter, ExecutionHistory
from utils.script_runner import ScriptRunner
from config import logger

execution_bp = Blueprint('execution', __name__, url_prefix='/api/execution')

@execution_bp.route('/script/<int:script_id>', methods=['POST'])
def execute_script(script_id):
    """执行单个脚本"""
    try:
        # 检查脚本是否存在
        script = Script.get(script_id)
        if not script:
            return jsonify({
                'code': 404,
                'message': f'脚本不存在: ID={script_id}',
                'data': None
            }), 404
        
        # 获取参数
        params = request.json or {}
        
        # 获取执行方式，是否使用Docker
        use_docker = params.pop('use_docker', None)  # 从参数中移除use_docker，避免传递给脚本
        
        # 验证必填参数
        if script.get('parameters'):
            for param in script['parameters']:
                if param['is_required'] and param['name'] not in params:
                    if not param.get('default_value'):
                        return jsonify({
                            'code': 400,
                            'message': f'缺少必填参数: {param["name"]}',
                            'data': None
                        }), 400
                    else:
                        # 使用默认值
                        params[param['name']] = param['default_value']
        
        # 创建执行历史记录
        history_id = ExecutionHistory.add(
            script_id=script_id,
            status="running",
            params=params
        )
        
        if not history_id:
            return jsonify({
                'code': 500,
                'message': '创建执行历史记录失败',
                'data': None
            }), 500
        
        # 使用RealtimeExecutor异步执行
        from utils.realtime_executor import RealtimeExecutor
        executor = RealtimeExecutor(history_id, script_path=script['file_path'], params=params)
        success = executor.execute()
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '启动脚本执行失败',
                'data': {
                    'history_id': history_id
                }
            }), 500
        
        # 立即返回执行ID，不等待执行完成
        return jsonify({
            'code': 0,
            'message': '脚本执行请求已提交',
            'data': {
                'history_id': history_id
            }
        })
    except Exception as e:
        logger.error(f"执行脚本失败: {str(e)}")
        
        # 尝试更新执行历史记录
        if locals().get('history_id'):
            try:
                ExecutionHistory.update(history_id, "failed", None, str(e))
            except:
                pass
        
        return jsonify({
            'code': 500,
            'message': f'执行脚本失败: {str(e)}',
            'data': None
        }), 500

@execution_bp.route('/chain/<int:chain_id>', methods=['POST'])
def execute_chain(chain_id):
    """执行脚本链"""
    try:
        from models import ScriptChain, ChainNode
        
        # 检查脚本链是否存在
        chain = ScriptChain.get(chain_id)
        if not chain:
            return jsonify({
                'code': 404,
                'message': f'脚本链不存在: ID={chain_id}',
                'data': None
            }), 404
        
        # 获取脚本链节点
        nodes = chain.get('nodes', [])
        if not nodes:
            return jsonify({
                'code': 400,
                'message': '脚本链中没有节点',
                'data': None
            }), 400
        
        # 获取参数
        params = request.json or {}
        
        # 获取执行方式，是否使用Docker
        use_docker = params.pop('use_docker', None)  # 从参数中移除use_docker，避免传递给脚本
        
        # 创建执行历史记录
        history_id = ExecutionHistory.add(
            chain_id=chain_id,
            status="running",
            params=params
        )
        
        if not history_id:
            return jsonify({
                'code': 500,
                'message': '创建执行历史记录失败',
                'data': None
            }), 500
        
        # 获取所有脚本详情
        scripts = {}
        for node in nodes:
            script_id = node['script_id']
            if script_id not in scripts:
                script = Script.get(script_id)
                if not script:
                    # 更新执行历史记录
                    ExecutionHistory.update(
                        history_id, 
                        "failed", 
                        None, 
                        f"脚本不存在: ID={script_id}"
                    )
                    
                    return jsonify({
                        'code': 404,
                        'message': f'脚本不存在: ID={script_id}',
                        'data': None
                    }), 404
                
                scripts[script_id] = script
            
            # 添加文件路径到节点
            node['file_path'] = scripts[script_id]['file_path']
        
        # 使用RealtimeExecutor异步执行脚本链
        from utils.realtime_executor import RealtimeExecutor
        executor = RealtimeExecutor(history_id, chain_nodes=nodes, params=params)
        success = executor.execute()
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '启动脚本链执行失败',
                'data': {
                    'history_id': history_id
                }
            }), 500
        
        # 立即返回执行ID，不等待执行完成
        return jsonify({
            'code': 0,
            'message': '脚本链执行请求已提交',
            'data': {
                'history_id': history_id
            }
        })
    except Exception as e:
        logger.error(f"执行脚本链失败: {str(e)}")
        
        # 尝试更新执行历史记录
        if locals().get('history_id'):
            try:
                ExecutionHistory.update(history_id, "failed", None, str(e))
            except:
                pass
        
        return jsonify({
            'code': 500,
            'message': f'执行脚本链失败: {str(e)}',
            'data': None
        }), 500

@execution_bp.route('/history', methods=['GET'])
def get_history_list():
    """获取执行历史列表"""
    try:
        # 获取参数
        limit = request.args.get('limit', 50, type=int)
        
        # 获取执行历史列表
        histories = ExecutionHistory.get_all(limit)
        
        return jsonify({
            'code': 0,
            'message': '获取执行历史列表成功',
            'data': histories
        })
    except Exception as e:
        logger.error(f"获取执行历史列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取执行历史列表失败: {str(e)}',
            'data': None
        }), 500

@execution_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取执行统计数据"""
    try:
        # 获取参数
        period = request.args.get('period', 'day')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        script_id = request.args.get('script_id', type=int)
        chain_id = request.args.get('chain_id', type=int)
        
        # 获取统计数据
        statistics = ExecutionHistory.get_statistics(
            period=period,
            start_date=start_date,
            end_date=end_date,
            script_id=script_id,
            chain_id=chain_id
        )
        
        return jsonify({
            'code': 0,
            'message': '获取执行统计数据成功',
            'data': statistics
        })
    except Exception as e:
        logger.error(f"获取执行统计数据失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取执行统计数据失败: {str(e)}',
            'data': None
        }), 500

@execution_bp.route('/history/<int:history_id>', methods=['GET'])
def get_history(history_id):
    """获取执行历史详情"""
    try:
        # 获取执行历史详情
        history = ExecutionHistory.get(history_id)
        
        if not history:
            return jsonify({
                'code': 404,
                'message': f'执行历史记录不存在: ID={history_id}',
                'data': None
            }), 404
        
        return jsonify({
            'code': 0,
            'message': '获取执行历史详情成功',
            'data': history
        })
    except Exception as e:
        logger.error(f"获取执行历史详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取执行历史详情失败: {str(e)}',
            'data': None
        }), 500
