# -*- coding: utf-8 -*-
"""
脚本链相关路由
提供脚本链创建、查询、修改、删除等接口
"""
import json
from flask import Blueprint, request, jsonify
from models import ScriptChain, ChainNode, Script
from config import logger

chain_bp = Blueprint('chains', __name__, url_prefix='/api/chains')

@chain_bp.route('', methods=['GET'])
def get_chains():
    """获取所有脚本链列表"""
    try:
        chains = ScriptChain.get_all()
        return jsonify({
            'code': 0,
            'message': '获取脚本链列表成功',
            'data': chains
        })
    except Exception as e:
        logger.error(f"获取脚本链列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取脚本链列表失败: {str(e)}',
            'data': None
        }), 500

@chain_bp.route('/<int:chain_id>', methods=['GET'])
def get_chain(chain_id):
    """获取脚本链详情"""
    try:
        chain = ScriptChain.get(chain_id)
        if not chain:
            return jsonify({
                'code': 404,
                'message': f'脚本链不存在: ID={chain_id}',
                'data': None
            }), 404
        
        return jsonify({
            'code': 0,
            'message': '获取脚本链详情成功',
            'data': chain
        })
    except Exception as e:
        logger.error(f"获取脚本链详情失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取脚本链详情失败: {str(e)}',
            'data': None
        }), 500

@chain_bp.route('', methods=['POST'])
def add_chain():
    """添加新脚本链"""
    try:
        # 获取参数
        data = request.json or {}
        name = data.get('name')
        description = data.get('description', '')
        nodes = data.get('nodes', [])
        
        # 验证必填参数
        if not name:
            return jsonify({
                'code': 400,
                'message': '脚本链名称不能为空',
                'data': None
            }), 400
        
        # 添加脚本链
        chain_id = ScriptChain.add(name, description)
        
        if not chain_id:
            return jsonify({
                'code': 500,
                'message': '添加脚本链失败',
                'data': None
            }), 500
        
        # 添加脚本链节点
        if nodes:
            for i, node in enumerate(nodes):
                script_id = node.get('script_id')
                
                # 检查脚本是否存在
                script = Script.get(script_id)
                if not script:
                    # 删除已创建的脚本链
                    ScriptChain.delete(chain_id)
                    
                    return jsonify({
                        'code': 404,
                        'message': f'脚本不存在: ID={script_id}',
                        'data': None
                    }), 404
                
                # 添加节点
                node_id = ChainNode.add(chain_id, script_id, i+1)
                
                if not node_id:
                    # 删除已创建的脚本链
                    ScriptChain.delete(chain_id)
                    
                    return jsonify({
                        'code': 500,
                        'message': f'添加脚本链节点失败: script_id={script_id}',
                        'data': None
                    }), 500
        
        # 获取完整的脚本链信息
        chain = ScriptChain.get(chain_id)
        
        return jsonify({
            'code': 0,
            'message': '添加脚本链成功',
            'data': chain
        })
    except Exception as e:
        logger.error(f"添加脚本链失败: {str(e)}")
        
        # 尝试删除已创建的脚本链
        if locals().get('chain_id'):
            try:
                ScriptChain.delete(chain_id)
            except:
                pass
        
        return jsonify({
            'code': 500,
            'message': f'添加脚本链失败: {str(e)}',
            'data': None
        }), 500

@chain_bp.route('/<int:chain_id>', methods=['PUT'])
def update_chain(chain_id):
    """更新脚本链信息"""
    try:
        # 检查脚本链是否存在
        chain = ScriptChain.get(chain_id)
        if not chain:
            return jsonify({
                'code': 404,
                'message': f'脚本链不存在: ID={chain_id}',
                'data': None
            }), 404
        
        # 获取更新数据
        data = request.json or {}
        name = data.get('name')
        description = data.get('description')
        nodes = data.get('nodes')
        
        # 更新脚本链信息
        success = ScriptChain.update(chain_id, name, description)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '更新脚本链信息失败',
                'data': None
            }), 500
        
        # 更新脚本链节点
        if nodes is not None:
            # 删除现有节点
            old_nodes = ChainNode.get_by_chain(chain_id)
            for old_node in old_nodes:
                ChainNode.delete(old_node['id'])
            
            # 添加新节点
            for i, node in enumerate(nodes):
                script_id = node.get('script_id')
                
                # 检查脚本是否存在
                script = Script.get(script_id)
                if not script:
                    return jsonify({
                        'code': 404,
                        'message': f'脚本不存在: ID={script_id}',
                        'data': None
                    }), 404
                
                # 添加节点
                node_id = ChainNode.add(chain_id, script_id, i+1)
                
                if not node_id:
                    return jsonify({
                        'code': 500,
                        'message': f'更新脚本链节点失败: script_id={script_id}',
                        'data': None
                    }), 500
        
        # 获取更新后的脚本链信息
        updated_chain = ScriptChain.get(chain_id)
        
        return jsonify({
            'code': 0,
            'message': '更新脚本链成功',
            'data': updated_chain
        })
    except Exception as e:
        logger.error(f"更新脚本链失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'更新脚本链失败: {str(e)}',
            'data': None
        }), 500

@chain_bp.route('/<int:chain_id>', methods=['DELETE'])
def delete_chain(chain_id):
    """删除脚本链"""
    try:
        # 检查脚本链是否存在
        chain = ScriptChain.get(chain_id)
        if not chain:
            return jsonify({
                'code': 404,
                'message': f'脚本链不存在: ID={chain_id}',
                'data': None
            }), 404
        
        # 软删除脚本链
        success = ScriptChain.delete(chain_id)
        
        if not success:
            return jsonify({
                'code': 500,
                'message': '删除脚本链失败',
                'data': None
            }), 500
        
        return jsonify({
            'code': 0,
            'message': '删除脚本链成功',
            'data': None
        })
    except Exception as e:
        logger.error(f"删除脚本链失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'删除脚本链失败: {str(e)}',
            'data': None
        }), 500
