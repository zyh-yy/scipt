#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统信息脚本
输出基本的系统信息，不需要任何参数
"""
import os
import sys
import platform
import json
import datetime
import socket
import psutil

def get_system_info():
    """获取系统信息"""
    try:
        # 获取系统基本信息
        system_info = {
            "system": platform.system(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": socket.gethostname(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_usage": [],
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 获取磁盘使用情况
        for part in psutil.disk_partitions(all=False):
            if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                # 跳过 CD-ROM 驱动器和不可用磁盘
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                system_info["disk_usage"].append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "percent": usage.percent
                })
            except PermissionError:
                continue
        
        return True, system_info, None
        
    except Exception as e:
        return False, None, str(e)

def main():
    """主函数"""
    # 读取参数文件路径
    if len(sys.argv) > 1:
        params_file = sys.argv[1]
        
        # 虽然脚本不需要参数，但仍然需要遵循执行规范，读取参数文件
        try:
            with open(params_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
        except Exception as e:
            print(json.dumps({"error": f"读取参数文件失败: {str(e)}"}))
            return 1
    
    # 获取系统信息
    success, info, error = get_system_info()
    
    if not success:
        print(json.dumps({"error": error}))
        return 1
    
    # 输出结果（JSON格式）
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
