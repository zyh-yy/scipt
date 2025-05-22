#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板 - 带参数，文件输出

此脚本演示如何处理输入参数并将结果写入文件
"""
import sys
import json
import os
import tempfile

def main():
    """主函数"""
    # 检查参数文件是否存在
    if len(sys.argv) < 2:
        print("参数文件不存在", file=sys.stderr)
        return 1
    
    params_file = sys.argv[1]
    if not os.path.exists(params_file):
        print(f"参数文件不存在: {params_file}", file=sys.stderr)
        return 1
    
    # 读取参数
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except Exception as e:
        print(f"读取参数失败: {str(e)}", file=sys.stderr)
        return 1
    
    # 处理参数
    name = params.get('name', 'World')
    value = params.get('value', 42)
    
    # 检查是否有上一个脚本的输出
    prev_output = params.get('__prev_output')
    
    # 处理业务逻辑
    result = {
        "message": f"Hello, {name}!",
        "value": value * 2,
        "prev_output": prev_output
    }
    
    # 创建输出文件
    output_file = tempfile.mktemp(suffix='.json')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 打印输出文件路径，系统会读取该文件内容
        print(output_file)
        return 0
    except Exception as e:
        print(f"写入输出文件失败: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
