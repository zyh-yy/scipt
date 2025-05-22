#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将脚本链测试相关信息插入数据库

此脚本用于将chain_test_1_generate.py、chain_test_2_process.py、chain_test_3_report.py
三个脚本的信息以及它们组成的脚本链信息插入到数据库中

脚本执行过程:
1. 检查三个测试脚本是否存在
2. 将三个脚本信息添加到数据库
3. 为每个脚本添加相应的参数信息
4. 创建脚本链并添加节点关系
"""

import os
import sys
import json
import datetime

# 添加项目根目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 导入数据库模型类
from backend.models import Script, ScriptParameter, ScriptChain, ChainNode, ExecutionHistory, initialize_db

def main():
    """主函数"""
    print(json.dumps({
        "status": "开始",
        "message": "开始将脚本链测试数据插入数据库",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 检查脚本文件是否存在
    script_files = [
        "scripts/chain_test_1_generate.py",
        "scripts/chain_test_2_process.py",
        "scripts/chain_test_3_report.py"
    ]
    
    for script_file in script_files:
        if not os.path.exists(script_file):
            print(json.dumps({
                "status": "错误",
                "message": f"脚本文件 {script_file} 不存在",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return 1
    
    # 确保数据库初始化
    initialize_db()
    
    try:
        # 添加脚本信息到数据库
        script_ids = add_scripts_to_db()
        
        if not all(script_ids):
            print(json.dumps({
                "status": "错误",
                "message": "添加脚本信息失败",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return 1
        
        # 添加脚本参数
        add_parameters_to_db(script_ids)
        
        # 创建脚本链
        chain_id = create_script_chain(script_ids)
        
        if not chain_id:
            print(json.dumps({
                "status": "错误",
                "message": "创建脚本链失败",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return 1
        
        print(json.dumps({
            "status": "成功",
            "message": "脚本链测试数据插入数据库成功",
            "data": {
                "scripts": script_ids,
                "chain_id": chain_id
            },
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        
        return 0
        
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "异常",
            "message": f"发生异常: {str(e)}",
            "traceback": traceback.format_exc(),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        return 1

def add_scripts_to_db():
    """添加脚本信息到数据库"""
    print(json.dumps({
        "status": "进行中",
        "message": "添加脚本信息到数据库",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 脚本信息
    scripts_info = [
        {
            "name": "数据生成器",
            "description": "脚本链测试 - 第1步：数据生成，用于测试脚本链执行能力，生成测试数据",
            "file_path": "scripts/chain_test_1_generate.py",
            "file_type": "python"
        },
        {
            "name": "数据处理器",
            "description": "脚本链测试 - 第2步：数据处理，用于测试脚本链执行能力，处理由第一步生成的数据",
            "file_path": "scripts/chain_test_2_process.py",
            "file_type": "python"
        },
        {
            "name": "结果汇总器",
            "description": "脚本链测试 - 第3步：结果汇总，用于测试脚本链执行能力，汇总前两步的结果并生成报告",
            "file_path": "scripts/chain_test_3_report.py",
            "file_type": "python"
        }
    ]
    
    script_ids = []
    
    for script_info in scripts_info:
        # 检查脚本是否已存在
        existing_scripts = Script.get_all()
        existing_script = next(
            (s for s in existing_scripts if s['file_path'] == script_info['file_path']),
            None
        )
        
        if existing_script:
            print(json.dumps({
                "status": "信息",
                "message": f"脚本 {script_info['name']} 已存在，ID: {existing_script['id']}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            script_ids.append(existing_script['id'])
        else:
            # 添加新脚本
            script_id = Script.add(
                script_info['name'],
                script_info['description'],
                script_info['file_path'],
                script_info['file_type']
            )
            
            if script_id:
                print(json.dumps({
                    "status": "信息",
                    "message": f"添加脚本 {script_info['name']} 成功，ID: {script_id}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                script_ids.append(script_id)
            else:
                print(json.dumps({
                    "status": "错误",
                    "message": f"添加脚本 {script_info['name']} 失败",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
                script_ids.append(None)
    
    return script_ids

def add_parameters_to_db(script_ids):
    """为脚本添加参数信息"""
    if not all(script_ids):
        return False
    
    print(json.dumps({
        "status": "进行中",
        "message": "为脚本添加参数信息",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 第一个脚本的参数 (数据生成器)
    generator_params = [
        {
            "name": "data_type",
            "description": "要生成的数据类型，支持sensor(传感器数据)、transaction(交易数据)、log(日志数据)",
            "param_type": "string",
            "is_required": 1,
            "default_value": "sensor"
        },
        {
            "name": "count",
            "description": "要生成的数据条数",
            "param_type": "integer",
            "is_required": 0,
            "default_value": "100"
        },
        {
            "name": "error_rate",
            "description": "模拟错误数据的比率(0-100)",
            "param_type": "float",
            "is_required": 0,
            "default_value": "5"
        },
        {
            "name": "output_file",
            "description": "输出文件路径，如果不指定则只输出到控制台",
            "param_type": "string",
            "is_required": 0,
            "default_value": ""
        }
    ]
    
    # 第二个脚本的参数 (数据处理器)
    processor_params = [
        {
            "name": "__prev_output",
            "description": "上一步骤的输出数据，由系统自动传递",
            "param_type": "json",
            "is_required": 1,
            "default_value": ""
        },
        {
            "name": "anomaly_detection",
            "description": "是否执行异常检测",
            "param_type": "boolean",
            "is_required": 0,
            "default_value": "true"
        },
        {
            "name": "analysis_level",
            "description": "分析级别: basic, standard, advanced",
            "param_type": "string",
            "is_required": 0,
            "default_value": "standard"
        },
        {
            "name": "output_file",
            "description": "输出文件路径，如果不指定则只输出到控制台",
            "param_type": "string",
            "is_required": 0,
            "default_value": ""
        }
    ]
    
    # 第三个脚本的参数 (结果汇总器)
    reporter_params = [
        {
            "name": "__prev_output",
            "description": "上一步骤的输出数据，由系统自动传递",
            "param_type": "json",
            "is_required": 1,
            "default_value": ""
        },
        {
            "name": "report_format",
            "description": "报告格式: json, summary",
            "param_type": "string",
            "is_required": 0,
            "default_value": "json"
        },
        {
            "name": "include_visualization",
            "description": "是否包含可视化代码",
            "param_type": "boolean",
            "is_required": 0,
            "default_value": "false"
        },
        {
            "name": "threshold",
            "description": "用于阈值分析的值",
            "param_type": "float",
            "is_required": 0,
            "default_value": ""
        },
        {
            "name": "output_file",
            "description": "输出文件路径，如果不指定则只输出到控制台",
            "param_type": "string",
            "is_required": 0,
            "default_value": ""
        }
    ]
    
    # 所有脚本的参数列表
    all_params = [generator_params, processor_params, reporter_params]
    
    # 为每个脚本添加参数
    for i, script_id in enumerate(script_ids):
        # 获取当前脚本的参数
        current_params = ScriptParameter.get_by_script(script_id)
        
        # 如果已有参数，检查是否需要更新
        if current_params:
            print(json.dumps({
                "status": "信息",
                "message": f"脚本 ID {script_id} 已有 {len(current_params)} 个参数",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            continue
        
        # 添加参数
        for param in all_params[i]:
            param_id = ScriptParameter.add(
                script_id,
                param['name'],
                param['description'],
                param['param_type'],
                param['is_required'],
                param['default_value']
            )
            
            if param_id:
                print(json.dumps({
                    "status": "信息",
                    "message": f"为脚本 ID {script_id} 添加参数 {param['name']} 成功，参数ID: {param_id}",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({
                    "status": "警告",
                    "message": f"为脚本 ID {script_id} 添加参数 {param['name']} 失败",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, ensure_ascii=False, indent=2))
    
    return True

def create_script_chain(script_ids):
    """创建脚本链并添加节点"""
    if not all(script_ids):
        return None
    
    print(json.dumps({
        "status": "进行中",
        "message": "创建脚本链并添加节点",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }, ensure_ascii=False, indent=2))
    
    # 检查是否已存在相同的脚本链
    existing_chains = ScriptChain.get_all()
    chain_name = "脚本链测试 - 三步流程"
    existing_chain = next((c for c in existing_chains if c['name'] == chain_name), None)
    
    if existing_chain:
        print(json.dumps({
            "status": "信息",
            "message": f"脚本链 '{chain_name}' 已存在，ID: {existing_chain['id']}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
        
        # 获取现有节点，检查是否需要更新
        existing_nodes = ChainNode.get_by_chain(existing_chain['id'])
        
        # 如果节点数量和顺序都一致，不需要更新
        if (len(existing_nodes) == 3 and
            existing_nodes[0]['script_id'] == script_ids[0] and
            existing_nodes[1]['script_id'] == script_ids[1] and
            existing_nodes[2]['script_id'] == script_ids[2]):
            
            print(json.dumps({
                "status": "信息",
                "message": "脚本链节点已存在且顺序正确，无需更新",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return existing_chain['id']
        
        # 删除现有节点，准备重新添加
        for node in existing_nodes:
            ChainNode.delete(node['id'])
            print(json.dumps({
                "status": "信息",
                "message": f"删除节点 ID: {node['id']}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        
        chain_id = existing_chain['id']
    else:
        # 创建新的脚本链
        chain_description = """
        脚本链测试三步流程：数据生成 -> 数据处理 -> 结果汇总
        
        第1步：数据生成 - 产生传感器、交易或日志数据
        第2步：数据处理 - 处理数据并进行分析
        第3步：结果汇总 - 生成报告和可视化结果
        """
        
        chain_id = ScriptChain.add(chain_name, chain_description)
        
        if not chain_id:
            print(json.dumps({
                "status": "错误",
                "message": "创建脚本链失败",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return None
        
        print(json.dumps({
            "status": "信息",
            "message": f"创建脚本链 '{chain_name}' 成功，ID: {chain_id}",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, ensure_ascii=False, indent=2))
    
    # 添加脚本链节点
    for i, script_id in enumerate(script_ids):
        node_id = ChainNode.add(chain_id, script_id, i + 1)
        
        if node_id:
            print(json.dumps({
                "status": "信息",
                "message": f"添加脚本链节点成功，脚本ID: {script_id}, 顺序: {i + 1}, 节点ID: {node_id}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "status": "错误",
                "message": f"添加脚本链节点失败，脚本ID: {script_id}, 顺序: {i + 1}",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False, indent=2))
            return None
    
    return chain_id

if __name__ == "__main__":
    sys.exit(main())
