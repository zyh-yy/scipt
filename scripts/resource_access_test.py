#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源访问测试脚本
用于测试Docker容器中的系统资源访问能力
"""
import sys
import json
import os
import tempfile
import shutil
import datetime
import platform

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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
    
    results = {
        "script_type": "资源访问测试",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params_received": params,
        "tests": {}
    }
    
    # 测试1: 文件系统访问
    try:
        results["tests"]["file_system"] = test_file_system()
    except Exception as e:
        results["tests"]["file_system"] = {"error": str(e), "success": False}
    
    # 测试2: 系统资源使用情况
    try:
        results["tests"]["system_resources"] = test_system_resources()
    except Exception as e:
        results["tests"]["system_resources"] = {"error": str(e), "success": False}
    
    # 测试3: 进程信息
    try:
        results["tests"]["process_info"] = test_process_info()
    except Exception as e:
        results["tests"]["process_info"] = {"error": str(e), "success": False}
    
    # 测试4: 系统目录读取
    try:
        results["tests"]["system_directories"] = test_system_directories()
    except Exception as e:
        results["tests"]["system_directories"] = {"error": str(e), "success": False}
    
    # 输出所有测试结果
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0

def test_file_system():
    """测试文件系统访问"""
    result = {"success": True}
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    result["temp_dir"] = temp_dir
    
    # 创建测试文件
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    test_content = f"测试文件内容 - 创建于 {datetime.datetime.now().isoformat()}"
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 验证文件创建成功
    if os.path.exists(test_file_path):
        result["file_created"] = True
        
        # 读取文件内容
        with open(test_file_path, 'r', encoding='utf-8') as f:
            read_content = f.read()
        
        # 验证内容正确
        result["content_verified"] = read_content == test_content
    else:
        result["file_created"] = False
    
    # 获取文件属性
    file_stat = os.stat(test_file_path)
    result["file_size"] = file_stat.st_size
    result["file_permissions"] = oct(file_stat.st_mode)[-3:]
    
    # 测试目录列表
    dir_contents = os.listdir(temp_dir)
    result["dir_contents"] = dir_contents
    
    # 清理临时文件和目录
    try:
        os.remove(test_file_path)
        os.rmdir(temp_dir)
        result["cleanup_success"] = True
    except Exception as e:
        result["cleanup_success"] = False
        result["cleanup_error"] = str(e)
    
    return result

def test_system_resources():
    """测试系统资源使用情况"""
    result = {"success": True}
    
    # 检查psutil是否可用
    result["psutil_available"] = PSUTIL_AVAILABLE
    
    if PSUTIL_AVAILABLE:
        # CPU信息
        result["cpu_count"] = psutil.cpu_count()
        result["cpu_percent"] = psutil.cpu_percent(interval=1)
        
        # 内存信息
        memory = psutil.virtual_memory()
        result["memory"] = {
            "total_mb": memory.total / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "used_mb": memory.used / (1024 * 1024),
            "percent": memory.percent
        }
        
        # 磁盘信息
        disk = psutil.disk_usage('/')
        result["disk"] = {
            "total_gb": disk.total / (1024 * 1024 * 1024),
            "used_gb": disk.used / (1024 * 1024 * 1024),
            "free_gb": disk.free / (1024 * 1024 * 1024),
            "percent": disk.percent
        }
    else:
        # 使用基本OS命令获取部分信息
        result["platform"] = platform.platform()
        result["python_version"] = sys.version
        result["cpu_info"] = platform.processor()
        
        # 尝试通过文件读取CPU核心数
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_cores = len([line for line in f if line.startswith('processor')])
                result["cpu_cores_from_proc"] = cpu_cores
        except:
            result["cpu_cores_from_proc"] = "无法获取"
        
        # 尝试通过文件读取内存信息
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    key, value = line.split(':', 1)
                    meminfo[key.strip()] = value.strip()
                
                result["meminfo_from_proc"] = {
                    "MemTotal": meminfo.get("MemTotal", "未知"),
                    "MemFree": meminfo.get("MemFree", "未知"),
                    "MemAvailable": meminfo.get("MemAvailable", "未知")
                }
        except:
            result["meminfo_from_proc"] = "无法获取"
    
    return result

def test_process_info():
    """测试进程信息获取"""
    result = {"success": True}
    
    # 获取当前进程信息
    result["current_process"] = {
        "pid": os.getpid(),
        "ppid": os.getppid() if hasattr(os, 'getppid') else None,
        "executable": sys.executable,
        "cwd": os.getcwd()
    }
    
    # 使用psutil获取详细进程信息
    if PSUTIL_AVAILABLE:
        current_process = psutil.Process()
        result["process_details"] = {
            "name": current_process.name(),
            "create_time": datetime.datetime.fromtimestamp(current_process.create_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": current_process.cpu_percent(interval=0.1),
            "memory_mb": current_process.memory_info().rss / (1024 * 1024),
            "status": current_process.status()
        }
        
        # 获取部分运行中的进程列表
        processes = []
        for proc in psutil.process_iter(attrs=['pid', 'name', 'username']):
            try:
                processes.append(proc.info)
                # 只获取前10个进程
                if len(processes) >= 10:
                    break
            except:
                pass
        
        result["running_processes_sample"] = processes
    else:
        # 尝试使用基本命令获取进程信息
        try:
            import subprocess
            ps_output = subprocess.check_output(["ps", "aux"], universal_newlines=True)
            result["ps_output_sample"] = ps_output.split('\n')[:10]
        except:
            result["ps_output_sample"] = "无法获取"
    
    return result

def test_system_directories():
    """测试系统目录读取"""
    result = {"success": True, "directory_tests": []}
    
    # 测试一些关键系统目录
    test_dirs = [
        "/etc",
        "/var/log",
        "/tmp",
        "/usr/bin",
        "/app"  # Docker容器中的应用目录
    ]
    
    for directory in test_dirs:
        dir_result = {
            "path": directory,
            "exists": os.path.exists(directory),
            "is_dir": os.path.isdir(directory) if os.path.exists(directory) else False
        }
        
        if dir_result["exists"] and dir_result["is_dir"]:
            try:
                contents = os.listdir(directory)
                dir_result["readable"] = True
                dir_result["contents_sample"] = contents[:5] if contents else []
                dir_result["count"] = len(contents)
            except Exception as e:
                dir_result["readable"] = False
                dir_result["error"] = str(e)
        
        result["directory_tests"].append(dir_result)
    
    return result

if __name__ == "__main__":
    sys.exit(main())
