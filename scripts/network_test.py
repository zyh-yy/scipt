#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络测试脚本
用于测试Docker容器中的网络连接能力
"""
import sys
import json
import os
import socket
import subprocess
import urllib.request
import urllib.error
import time
import datetime
import platform

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
    
    # 获取要测试的目标
    urls = params.get("urls", ["http://www.baidu.com", "http://www.qq.com", "http://example.com"])
    hosts = params.get("hosts", ["www.baidu.com", "www.qq.com", "8.8.8.8"])
    ports = params.get("ports", [80, 443, 8080])
    
    results = {
        "script_type": "网络测试",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params_received": params,
        "system_info": {
            "hostname": socket.gethostname(),
            "platform": platform.platform()
        },
        "tests": {}
    }
    
    # 测试1: 基本网络配置
    try:
        results["tests"]["network_config"] = test_network_config()
    except Exception as e:
        results["tests"]["network_config"] = {"error": str(e), "success": False}
    
    # 测试2: DNS解析
    try:
        results["tests"]["dns_lookup"] = test_dns_lookup(hosts)
    except Exception as e:
        results["tests"]["dns_lookup"] = {"error": str(e), "success": False}
    
    # 测试3: HTTP请求
    try:
        results["tests"]["http_requests"] = test_http_requests(urls)
    except Exception as e:
        results["tests"]["http_requests"] = {"error": str(e), "success": False}
    
    # 测试4: 端口连接
    try:
        results["tests"]["port_check"] = test_port_check(hosts[0], ports)
    except Exception as e:
        results["tests"]["port_check"] = {"error": str(e), "success": False}
    
    # 测试5: Ping测试
    try:
        results["tests"]["ping_test"] = test_ping(hosts)
    except Exception as e:
        results["tests"]["ping_test"] = {"error": str(e), "success": False}
    
    # 输出所有测试结果
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0

def test_network_config():
    """测试基本网络配置"""
    result = {"success": True}
    
    # 获取主机名
    result["hostname"] = socket.gethostname()
    
    # 尝试获取IP地址
    try:
        result["ip_address"] = socket.gethostbyname(socket.gethostname())
    except:
        # 如果无法通过主机名获取IP，尝试其他方法
        try:
            # 创建一个临时socket连接到一个公共地址，获取本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            result["ip_address"] = s.getsockname()[0]
            s.close()
        except:
            result["ip_address"] = "无法获取"
    
    # 获取网络接口信息
    try:
        import netifaces
        result["interfaces"] = {}
        for interface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(interface)
            # 获取IPv4地址
            if netifaces.AF_INET in addrs:
                result["interfaces"][interface] = {
                    "ipv4": addrs[netifaces.AF_INET][0]["addr"],
                    "netmask": addrs[netifaces.AF_INET][0]["netmask"]
                }
    except ImportError:
        # 如果没有netifaces模块，尝试使用命令行工具
        try:
            if os.name == 'nt':  # Windows
                result["network_interfaces"] = "netifaces模块不可用，在Windows上无法获取接口信息"
            else:  # Linux/Unix
                ipconfig = subprocess.check_output(["ip", "addr"], universal_newlines=True)
                result["network_interfaces"] = "接口信息(来自ip addr命令):\n" + ipconfig[:500] + "..."
        except:
            result["network_interfaces"] = "无法获取网络接口信息"
    
    # 获取默认网关
    try:
        if os.name == 'nt':  # Windows
            result["default_gateway"] = "在Windows上无法通过脚本获取默认网关"
        else:  # Linux/Unix
            gateway = subprocess.check_output(["ip", "route", "show", "default"], universal_newlines=True).strip()
            result["default_gateway"] = gateway
    except:
        result["default_gateway"] = "无法获取默认网关"
    
    # 尝试获取DNS服务器
    try:
        if os.name == 'nt':  # Windows
            result["dns_servers"] = "在Windows上无法通过脚本获取DNS服务器"
        else:  # Linux/Unix
            # 尝试读取/etc/resolv.conf获取DNS信息
            dns_servers = []
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns_servers.append(line.split()[1])
            result["dns_servers"] = dns_servers
    except:
        result["dns_servers"] = "无法获取DNS服务器"
    
    return result

def test_dns_lookup(hosts):
    """测试DNS解析"""
    result = {"success": True, "lookups": []}
    
    for host in hosts:
        lookup = {"hostname": host}
        try:
            # 跳过已经是IP地址的情况
            if is_ip_address(host):
                lookup["is_ip"] = True
                lookup["success"] = True
                lookup["ip"] = host
            else:
                start_time = time.time()
                ip = socket.gethostbyname(host)
                elapsed_time = time.time() - start_time
                
                lookup["success"] = True
                lookup["ip"] = ip
                lookup["time_ms"] = round(elapsed_time * 1000, 2)
                
                # 尝试反向解析
                try:
                    hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
                    lookup["reverse_lookup"] = {
                        "hostname": hostname,
                        "aliases": aliaslist,
                        "ips": ipaddrlist
                    }
                except:
                    lookup["reverse_lookup"] = "失败"
        except Exception as e:
            lookup["success"] = False
            lookup["error"] = str(e)
        
        result["lookups"].append(lookup)
    
    return result

def test_http_requests(urls):
    """测试HTTP请求"""
    result = {"success": True, "requests": []}
    
    for url in urls:
        request = {"url": url}
        try:
            start_time = time.time()
            response = urllib.request.urlopen(url, timeout=10)
            elapsed_time = time.time() - start_time
            
            # 读取部分内容，不需要全部读取
            content = response.read(1024)
            
            request["success"] = True
            request["status_code"] = response.getcode()
            request["time_ms"] = round(elapsed_time * 1000, 2)
            request["headers"] = dict(response.getheaders())
            request["content_length"] = len(content)
            request["content_type"] = response.getheader("Content-Type")
        except Exception as e:
            request["success"] = False
            request["error"] = str(e)
        
        result["requests"].append(request)
    
    return result

def test_port_check(host, ports):
    """测试端口连接"""
    result = {"success": True, "port_checks": []}
    
    for port in ports:
        port_check = {"host": host, "port": port}
        try:
            start_time = time.time()
            
            # 创建套接字并尝试连接
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)  # 设置2秒超时
            connect_result = s.connect_ex((host, port))
            s.close()
            
            elapsed_time = time.time() - start_time
            
            if connect_result == 0:
                port_check["success"] = True
                port_check["status"] = "开放"
            else:
                port_check["success"] = False
                port_check["status"] = "关闭或被过滤"
                port_check["error_code"] = connect_result
            
            port_check["time_ms"] = round(elapsed_time * 1000, 2)
            
        except Exception as e:
            port_check["success"] = False
            port_check["status"] = "测试失败"
            port_check["error"] = str(e)
        
        result["port_checks"].append(port_check)
    
    return result

def test_ping(hosts):
    """执行Ping测试"""
    result = {"success": True, "pings": []}
    
    for host in hosts:
        ping_result = {"host": host}
        
        try:
            # 根据操作系统选择不同的ping命令参数
            if os.name == 'nt':  # Windows
                ping_count = "4"
                ping_cmd = ["ping", "-n", ping_count, "-w", "2000", host]
            else:  # Linux/Unix
                ping_count = "4"
                ping_cmd = ["ping", "-c", ping_count, "-W", "2", host]
            
            start_time = time.time()
            ping_output = subprocess.check_output(ping_cmd, universal_newlines=True)
            elapsed_time = time.time() - start_time
            
            # 解析ping输出
            ping_result["success"] = True
            ping_result["output"] = ping_output.strip()
            ping_result["total_time_ms"] = round(elapsed_time * 1000, 2)
            
            # 尝试提取平均时间
            try:
                if os.name == 'nt':  # Windows
                    # 提取Windows ping输出中的平均时间
                    for line in ping_output.split('\n'):
                        if "平均" in line or "Average" in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                avg_time = parts[1].strip().split('ms')[0].strip()
                                ping_result["avg_time_ms"] = float(avg_time)
                                break
                else:  # Linux/Unix
                    # 提取Linux ping输出中的平均时间
                    for line in ping_output.split('\n'):
                        if "min/avg/max" in line or "最小/平均/最大" in line:
                            parts = line.split('=')
                            if len(parts) > 1:
                                times = parts[1].strip().split('/')
                                if len(times) > 2:
                                    ping_result["avg_time_ms"] = float(times[1])
                                    break
            except:
                ping_result["avg_time_ms"] = "无法解析"
            
        except subprocess.CalledProcessError as e:
            ping_result["success"] = False
            ping_result["error"] = "Ping失败，可能主机不可达"
            ping_result["exit_code"] = e.returncode
            ping_result["output"] = e.output.strip() if hasattr(e, 'output') else "无输出"
        except Exception as e:
            ping_result["success"] = False
            ping_result["error"] = str(e)
        
        result["pings"].append(ping_result)
    
    return result

def is_ip_address(host):
    """检查是否是IP地址"""
    try:
        socket.inet_aton(host)
        return True
    except:
        return False

if __name__ == "__main__":
    sys.exit(main())
