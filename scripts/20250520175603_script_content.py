#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统信息获取脚本
获取当前系统的基本信息
"""
import os
import sys
import json
import platform
import psutil
import socket
import datetime

def get_system_info():
    """获取系统信息"""
    info = {
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_total": psutil.disk_usage('/').total,
        "disk_used": psutil.disk_usage('/').used,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return info

def main():
    """主函数"""
    try:
        # 处理参数
        params_file = None
        if len(sys.argv) > 1:
            params_file = sys.argv[1]
        
        # 读取参数文件
        params = {}
        if params_file and os.path.exists(params_file):
            with open(params_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
        
        # 获取系统信息
        system_info = get_system_info()
        
        # 根据参数进行过滤
        if 'filter' in params:
            filtered_info = {}
            filter_keys = params['filter'].split(',')
            for key in filter_keys:
                if key in system_info:
                    filtered_info[key] = system_info[key]
            result = filtered_info
        else:
            result = system_info
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        #print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
