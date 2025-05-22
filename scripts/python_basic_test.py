#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python基础测试脚本
用于测试基本的输入输出和系统信息获取
"""
import sys
import json
import os
import platform
import socket
import datetime

def main():
    # 检查参数文件
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数文件"}))
        return 1
    
    params_file = sys.argv[1]
    
    # 读取参数
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"参数读取失败: {str(e)}"}))
        return 1
    
    # 获取系统信息
    system_info = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": sys.version,
        "processor": platform.processor(),
        "docker": "可能在Docker中" if os.path.exists("/.dockerenv") else "未在Docker中运行"
    }
    
    # 获取环境变量
    env_vars = {key: value for key, value in os.environ.items()}
    
    # 获取当前目录
    current_dir = os.getcwd()
    try:
        dir_contents = os.listdir(current_dir)
    except:
        dir_contents = ["无法列出目录内容"]
    
    # 输出测试结果
    result = {
        "script_type": "Python基础测试",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_info": system_info,
        "current_directory": current_dir,
        "directory_contents": dir_contents[:10],  # 只显示前10个文件/目录
        "params_received": params,
        "env_vars_sample": {k: env_vars[k] for k in list(env_vars.keys())[:10]},  # 只显示部分环境变量
        "message": "Python基础测试脚本执行成功"
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
