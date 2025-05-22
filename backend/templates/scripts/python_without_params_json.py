#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板 - 不带参数，JSON输出

此脚本演示如何返回JSON格式的结果
"""
import sys
import json
import os
import platform
import datetime

def main():
    """主函数"""
    # 处理业务逻辑
    # 示例：获取系统信息
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 以JSON格式返回结果
    print(json.dumps(system_info, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
