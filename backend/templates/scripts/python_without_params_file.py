#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本模板 - 不带参数，文件输出

此脚本演示如何将结果输出到文件
"""
import sys
import json
import os
import platform
import datetime
import tempfile

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
    
    # 创建输出文件
    output_file = tempfile.mktemp(suffix='.json')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(system_info, f, ensure_ascii=False, indent=2)
        
        # 打印输出文件路径，系统会读取该文件内容
        print(output_file)
        return 0
    except Exception as e:
        print(f"写入输出文件失败: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
