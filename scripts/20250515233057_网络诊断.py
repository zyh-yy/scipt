#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络诊断脚本
执行网络状态检查并生成诊断报告
"""
import os
import sys
import json
import socket
import subprocess
import platform
import datetime
import time

def ping(host, count=4):
    """Ping主机"""
    # 根据操作系统选择命令
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        ping_cmd = ['ping', '-n', str(count), host]
    else:
        ping_cmd = ['ping', '-c', str(count), host]
    
    try:
        # 执行命令
        process = subprocess.Popen(
            ping_cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        # 检查返回码
        success = process.returncode == 0
        
        return {
            "success": success,
            "command": " ".join(ping_cmd),
            "output": stdout,
            "error": stderr
        }
    except Exception as e:
        return {
            "success": False,
            "command": " ".join(ping_cmd),
            "output": "",
            "error": str(e)
        }

def check_dns(domain):
    """检查DNS解析"""
    try:
        ip = socket.gethostbyname(domain)
        return {
            "success": True,
            "domain": domain,
            "ip": ip
        }
    except Exception as e:
        return {
            "success": False,
            "domain": domain,
            "error": str(e)
        }

def check_port(host, port):
    """检查端口是否开放"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, int(port)))
        if result == 0:
            return {"success": True, "host": host, "port": port, "status": "open"}
        else:
            return {"success": False, "host": host, "port": port, "status": "closed", "error": f"连接失败，错误码: {result}"}
    except Exception as e:
        return {"success": False, "host": host, "port": port, "status": "error", "error": str(e)}
    finally:
        s.close()

def network_diagnostic(targets):
    """执行网络诊断"""
    results = {}
    
    # 诊断开始时间
    start_time = datetime.datetime.now()
    
    # 运行诊断
    for target in targets:
        target_type = target.get('type', 'ping')
        host = target.get('host', '')
        
        if not host:
            continue
        
        if target_type == 'ping':
            count = target.get('count', 4)
            results[f"ping_{host}"] = ping(host, count)
        elif target_type == 'dns':
            results[f"dns_{host}"] = check_dns(host)
        elif target_type == 'port':
            port = target.get('port', 80)
            results[f"port_{host}_{port}"] = check_port(host, port)
    
    # 诊断结束时间
    end_time = datetime.datetime.now()
    
    # 生成汇总报告
    summary = {
        "total_checks": len(results),
        "successful_checks": sum(1 for result in results.values() if result.get('success', False)),
        "failed_checks": sum(1 for result in results.values() if not result.get('success', False)),
        "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
        "duration_seconds": (end_time - start_time).total_seconds()
    }
    
    # 完整结果
    return {
        "summary": summary,
        "details": results,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

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
        
        # 获取目标列表
        targets = params.get('targets', [])
        
        # 如果没有提供目标，则使用默认值
        if not targets:
            targets = [
                {"type": "ping", "host": "8.8.8.8", "count": 4},
                {"type": "ping", "host": "www.baidu.com", "count": 4},
                {"type": "dns", "host": "www.google.com"},
                {"type": "port", "host": "www.baidu.com", "port": 80}
            ]
        
        # 执行网络诊断
        result = network_diagnostic(targets)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
