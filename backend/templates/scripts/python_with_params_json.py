#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板 - 带参数，JSON输出

此脚本演示如何处理标准化参数结构并以JSON格式返回结果
"""
import sys
import json
import os
from datetime import datetime

def main():
    """主函数"""
    # 检查参数文件是否存在
    if len(sys.argv) < 2:
        print(json.dumps({"error": "参数文件不存在"}))
        return 1
    
    params_file = sys.argv[1]
    if not os.path.exists(params_file):
        print(json.dumps({"error": f"参数文件不存在: {params_file}"}))
        return 1
    
    # 读取参数
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params_data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"读取参数失败: {str(e)}"}))
        return 1
    
    # 提取标准化参数结构
    user_params = params_data.get('user_params', {})
    system_params = params_data.get('system_params', {})
    file_params = params_data.get('file_params', {})
    
    # 从用户参数中提取具体值（添加默认值保护）
    name = user_params.get('name', 'World')
    value = user_params.get('value', 42)
    
    # 提取系统参数
    prev_output = system_params.get('__prev_output')
    execution_time = system_params.get('__execution_time')
    
    # 处理上一个脚本的输出（如果有）
    prev_result = None
    if prev_output:
        # 示例：从前一个脚本的输出中提取信息
        if isinstance(prev_output, dict):
            prev_result = prev_output.get('message', '无前序消息')
        else:
            prev_result = str(prev_output)
    
    # 处理业务逻辑
    result = {
        "message": f"Hello, {name}!",
        "value": value * 2,
        "processed_at": datetime.now().isoformat(),
        "status": "success"
    }
    
    # 添加前一个脚本的处理结果（如果有）
    if prev_result:
        result["prev_output_processed"] = True
        result["prev_result"] = prev_result
    
    # 以JSON格式返回结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
