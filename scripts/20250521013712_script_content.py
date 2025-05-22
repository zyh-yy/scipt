#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统资源监控脚本 - 带参数，JSON输出

此脚本根据输入参数监控系统资源并返回分析结果
参数:
- resource_type: 要监控的资源类型 (string)
- sample_count: 采样次数 (int)
"""
import sys
import json
import os
import psutil
import platform
import datetime
import socket
from time import sleep

def get_cpu_info(sample_count=1):
    """获取CPU使用率信息"""
    cpu_info = {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "usage_samples": []
    }
    
    # 采集CPU使用率样本
    for _ in range(sample_count):
        usage = psutil.cpu_percent(interval=1, percpu=True)
        avg_usage = sum(usage) / len(usage)
        cpu_info["usage_samples"].append({
            "per_cpu": usage,
            "average": round(avg_usage, 2)
        })
    
    # 计算平均使用率
    if sample_count > 0:
        total_avg = sum(sample["average"] for sample in cpu_info["usage_samples"]) / sample_count
        cpu_info["overall_average"] = round(total_avg, 2)
    
    return cpu_info

def get_memory_info(sample_count=1):
    """获取内存使用信息"""
    memory_info = {
        "samples": []
    }
    
    for _ in range(sample_count):
        mem = psutil.virtual_memory()
        memory_info["samples"].append({
            "total_gb": round(mem.total / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent": mem.percent,
            "timestamp": datetime.datetime.now().isoformat()
        })
        if sample_count > 1:
            sleep(1)
    
    return memory_info

def get_disk_info(sample_count=1):
    """获取磁盘使用信息"""
    disk_info = {
        "partitions": []
    }
    
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
            continue
        
        partition_info = {
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "samples": []
        }
        
        try:
            for _ in range(sample_count):
                usage = psutil.disk_usage(part.mountpoint)
                partition_info["samples"].append({
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                if sample_count > 1:
                    sleep(1)
        except PermissionError:
            continue
        
        disk_info["partitions"].append(partition_info)
    
    return disk_info

def get_network_info(sample_count=1):
    """获取网络使用信息"""
    network_info = {
        "interfaces": {}
    }
    
    # 获取初始状态
    net_io_counters_start = psutil.net_io_counters(pernic=True)
    
    for i in range(sample_count):
        # 等待1秒
        sleep(1)
        
        # 获取当前状态
        net_io_counters_current = psutil.net_io_counters(pernic=True)
        
        # 计算每秒网络流量
        for interface, counters_current in net_io_counters_current.items():
            if interface in net_io_counters_start:
                counters_prev = net_io_counters_start[interface]
                
                # 计算速率 (bytes/s)
                bytes_sent_per_sec = counters_current.bytes_sent - counters_prev.bytes_sent
                bytes_recv_per_sec = counters_current.bytes_recv - counters_prev.bytes_recv
                
                if interface not in network_info["interfaces"]:
                    network_info["interfaces"][interface] = {
                        "samples": []
                    }
                
                network_info["interfaces"][interface]["samples"].append({
                    "bytes_sent": counters_current.bytes_sent,
                    "bytes_recv": counters_current.bytes_recv,
                    "bytes_sent_per_sec": bytes_sent_per_sec,
                    "bytes_recv_per_sec": bytes_recv_per_sec,
                    "mb_sent_per_sec": round(bytes_sent_per_sec / (1024**2), 4),
                    "mb_recv_per_sec": round(bytes_recv_per_sec / (1024**2), 4),
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        # 更新起始状态为当前状态，用于下一次计算
        net_io_counters_start = net_io_counters_current
    
    return network_info

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
    
    # 从用户参数中提取具体值（添加默认值保护）
    resource_type = user_params.get('resource_type', 'cpu')  # 字符串参数
    sample_count = user_params.get('sample_count', 1)       # 整数参数
    
    # 验证参数
    try:
        sample_count = int(sample_count)
        if sample_count < 1:
            sample_count = 1
    except (ValueError, TypeError):
        sample_count = 1
    
    # 初始化结果
    result = {
        "hostname": socket.gethostname(),
        "system": platform.system(),
        "platform": platform.platform(),
        "timestamp": datetime.datetime.now().isoformat(),
        "parameters": {
            "resource_type": resource_type,
            "sample_count": sample_count
        }
    }
    
    # 根据资源类型收集信息
    if resource_type == 'cpu':
        result["cpu_info"] = get_cpu_info(sample_count)
    elif resource_type == 'memory':
        result["memory_info"] = get_memory_info(sample_count)
    elif resource_type == 'disk':
        result["disk_info"] = get_disk_info(sample_count)
    elif resource_type == 'network':
        result["network_info"] = get_network_info(sample_count)
    elif resource_type == 'all':
        result["cpu_info"] = get_cpu_info(sample_count)
        result["memory_info"] = get_memory_info(sample_count)
        result["disk_info"] = get_disk_info(sample_count)
        result["network_info"] = get_network_info(sample_count)
    else:
        result["error"] = f"不支持的资源类型: {resource_type}"
        result["supported_types"] = ["cpu", "memory", "disk", "network", "all"]
    
    # 以JSON格式返回结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
