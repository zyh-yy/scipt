#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板 - 带参数，无输出

此脚本演示如何处理输入参数但不返回结果
"""
import sys
import json
import os

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
    
    # 处理业务逻辑 - 无需输出结果
    # 例如，可以在这里执行一些不需要返回值的操作，如清理临时文件
    
    # 成功执行，无输出
    return 0

if __name__ == "__main__":
    sys.exit(main())
