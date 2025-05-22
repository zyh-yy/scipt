#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库示例数据填充脚本
用于为系统各个功能创建示例数据，便于展示页面效果
"""
import os
import sys
import json
import random
import datetime
import time
import sqlite3
from pathlib import Path

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.config import logger, UPLOAD_FOLDER
from backend.models.base import initialize_db, DBManager
from backend.models.script import Script, ScriptParameter, ScriptVersion
from backend.models.chain import ScriptChain, ChainNode
from backend.models.execution import ExecutionHistory, AlertConfig, AlertHistory
from backend.models.schedule import ScheduledTask


def create_sample_scripts():
    """创建示例脚本"""
    print("正在创建示例脚本...")
    
    # 确保上传目录存在
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    # 示例脚本1 - 系统信息获取脚本
    system_info_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
系统信息获取脚本
获取当前系统的基本信息
\"\"\"
import os
import sys
import json
import platform
import psutil
import socket
import datetime

def get_system_info():
    \"\"\"获取系统信息\"\"\"
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
    \"\"\"主函数\"\"\"
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
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    # 示例脚本2 - 文件生成脚本
    file_generator_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
文件生成脚本
根据指定的参数生成文件
\"\"\"
import os
import sys
import json
import random
import string
import datetime

def generate_random_string(length=10):
    \"\"\"生成随机字符串\"\"\"
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_text_file(file_path, size_kb=10, content_type='random'):
    \"\"\"生成文本文件\"\"\"
    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # 根据内容类型生成内容
    if content_type == 'random':
        content = generate_random_string(size_kb * 1024)
    elif content_type == 'timestamp':
        # 生成带时间戳的内容
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_content = f"Generated at {timestamp}\\n"
        content = base_content
        while len(content) < size_kb * 1024:
            content += generate_random_string(100) + "\\n"
    else:
        # 默认生成随机内容
        content = generate_random_string(size_kb * 1024)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {
        "file_path": file_path,
        "size_kb": size_kb,
        "content_type": content_type,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    \"\"\"主函数\"\"\"
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
        
        # 获取参数
        file_path = params.get('file_path', f"output_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        size_kb = int(params.get('size_kb', 10))
        content_type = params.get('content_type', 'random')
        
        # 检查是否有前一个脚本的输出
        prev_output = params.get('__prev_output', None)
        if prev_output and isinstance(prev_output, dict) and 'file_path' in prev_output:
            # 使用前一个脚本的输出路径作为基础
            base_dir = os.path.dirname(prev_output['file_path'])
            if base_dir:
                file_path = os.path.join(base_dir, os.path.basename(file_path))
        
        # 生成文件
        result = generate_text_file(file_path, size_kb, content_type)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    # 示例脚本3 - 日志分析脚本
    log_analyzer_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
日志分析脚本
分析日志文件并生成统计报告
\"\"\"
import os
import sys
import json
import re
import datetime
from collections import Counter

def analyze_log_file(file_path, pattern=None, time_window=None):
    \"\"\"分析日志文件\"\"\"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"日志文件不存在: {file_path}")
    
    # 设置默认正则表达式匹配ERROR, WARNING, INFO等级
    if not pattern:
        pattern = r'\\[(ERROR|WARNING|INFO|DEBUG)\\]'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.readlines()
    
    # 分析结果
    total_lines = len(log_content)
    matched_lines = []
    level_counts = Counter()
    
    # 编译正则表达式
    regex = re.compile(pattern)
    
    # 时间窗口筛选
    current_time = datetime.datetime.now()
    if time_window:
        window_minutes = int(time_window)
        cutoff_time = current_time - datetime.timedelta(minutes=window_minutes)
        # 尝试从日志中提取时间
        time_pattern = r'\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}'
        time_regex = re.compile(time_pattern)
    
    # 逐行分析
    for line in log_content:
        # 时间窗口筛选
        if time_window:
            time_match = time_regex.search(line)
            if time_match:
                try:
                    line_time = datetime.datetime.strptime(time_match.group(), '%Y-%m-%d %H:%M:%S')
                    if line_time < cutoff_time:
                        continue
                except:
                    pass
        
        # 匹配日志级别
        match = regex.search(line)
        if match:
            matched_lines.append(line.strip())
            # 如果匹配到日志级别，则计数
            if len(match.groups()) > 0:
                level = match.group(1)
                level_counts[level] += 1
    
    # 生成结果
    result = {
        "file_path": file_path,
        "total_lines": total_lines,
        "matched_lines": len(matched_lines),
        "level_counts": dict(level_counts),
        "sample_lines": matched_lines[:10],  # 只返回前10行作为样本
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return result

def main():
    \"\"\"主函数\"\"\"
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
        
        # 获取参数
        file_path = params.get('file_path')
        if not file_path:
            raise ValueError("必须提供日志文件路径参数 'file_path'")
        
        pattern = params.get('pattern')
        time_window = params.get('time_window')
        
        # 检查是否有前一个脚本的输出
        prev_output = params.get('__prev_output', None)
        if prev_output and isinstance(prev_output, dict) and 'file_path' in prev_output:
            # 使用前一个脚本的输出文件路径
            file_path = prev_output['file_path']
        
        # 分析日志
        result = analyze_log_file(file_path, pattern, time_window)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    # 示例脚本4 - 数据库备份脚本
    db_backup_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
数据库备份脚本
备份SQLite数据库到指定位置
\"\"\"
import os
import sys
import json
import shutil
import datetime
import sqlite3
import zipfile

def backup_sqlite_db(db_path, backup_dir=None, compress=True):
    \"\"\"备份SQLite数据库\"\"\"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    # 设置备份目录
    if not backup_dir:
        backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    
    # 创建备份目录（如果不存在）
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    db_name = os.path.basename(db_path)
    backup_name = f"{os.path.splitext(db_name)[0]}_{timestamp}.sqlite"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 复制数据库文件
    shutil.copy2(db_path, backup_path)
    
    # 如果需要压缩
    zip_path = None
    if compress:
        zip_name = f"{os.path.splitext(db_name)[0]}_{timestamp}.zip"
        zip_path = os.path.join(backup_dir, zip_name)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, arcname=backup_name)
        
        # 删除未压缩的备份
        os.remove(backup_path)
        backup_path = zip_path
    
    # 生成结果
    result = {
        "original_db": db_path,
        "backup_path": backup_path,
        "backup_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "compressed": compress
    }
    
    return result

def main():
    \"\"\"主函数\"\"\"
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
        
        # 获取参数
        db_path = params.get('db_path')
        if not db_path:
            # 如果没有提供数据库路径，则使用默认的项目数据库
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            db_path = os.path.join(project_root, 'database', 'scripts.db')
        
        backup_dir = params.get('backup_dir')
        compress = params.get('compress', True)
        
        # 备份数据库
        result = backup_sqlite_db(db_path, backup_dir, compress)
        
        # 输出结果
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""

    # 示例脚本5 - 网络诊断脚本
    network_diagnostic_script = """#!/usr/bin/env python
# -*- coding: utf-8 -*-
\"\"\"
网络诊断脚本
执行网络状态检查并生成诊断报告
\"\"\"
import os
import sys
import json
import socket
import subprocess
import platform
import datetime
import time

def ping(host, count=4):
    \"\"\"Ping主机\"\"\"
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
    \"\"\"检查DNS解析\"\"\"
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
    \"\"\"检查端口是否开放\"\"\"
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
    \"\"\"执行网络诊断\"\"\"
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
    \"\"\"主函数\"\"\"
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
"""

    # 保存示例脚本文件
    scripts_data = [
        {
            "name": "系统信息获取",
            "description": "获取当前系统的基本信息，包括主机名、IP地址、CPU使用率等",
            "content": system_info_script,
            "file_type": "py",
            "parameters": [
                {"name": "filter", "description": "筛选要输出的字段，以逗号分隔", "param_type": "string", "is_required": 0, "default_value": ""}
            ]
        },
        {
            "name": "文件生成器",
            "description": "生成指定大小和内容类型的文本文件",
            "content": file_generator_script,
            "file_type": "py",
            "parameters": [
                {"name": "file_path", "description": "输出文件路径", "param_type": "string", "is_required": 0, "default_value": ""},
                {"name": "size_kb", "description": "文件大小(KB)", "param_type": "number", "is_required": 0, "default_value": "10"},
                {"name": "content_type", "description": "内容类型：random或timestamp", "param_type": "string", "is_required": 0, "default_value": "random"}
            ]
        },
        {
            "name": "日志分析器",
            "description": "分析日志文件并生成统计报告",
            "content": log_analyzer_script,
            "file_type": "py",
            "parameters": [
                {"name": "file_path", "description": "日志文件路径", "param_type": "string", "is_required": 1, "default_value": ""},
                {"name": "pattern", "description": "匹配模式正则表达式", "param_type": "string", "is_required": 0, "default_value": ""},
                {"name": "time_window", "description": "时间窗口（分钟）", "param_type": "number", "is_required": 0, "default_value": ""}
            ]
        },
        {
            "name": "数据库备份",
            "description": "备份SQLite数据库到指定位置",
            "content": db_backup_script,
            "file_type": "py",
            "parameters": [
                {"name": "db_path", "description": "数据库文件路径", "param_type": "string", "is_required": 0, "default_value": ""},
                {"name": "backup_dir", "description": "备份目录", "param_type": "string", "is_required": 0, "default_value": ""},
                {"name": "compress", "description": "是否压缩备份", "param_type": "boolean", "is_required": 0, "default_value": "true"}
            ]
        },
        {
            "name": "网络诊断",
            "description": "执行网络状态检查并生成诊断报告",
            "content": network_diagnostic_script,
            "file_type": "py",
            "parameters": [
                {"name": "targets", "description": "诊断目标列表", "param_type": "json", "is_required": 0, "default_value": "[]"}
            ]
        }
    ]
    
    script_ids = []
    for script_data in scripts_data:
        # 保存脚本文件
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{script_data['name']}.{script_data['file_type']}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(script_data['content'])
        
        # 如果是Linux/Unix系统，给予执行权限
        if os.name != 'nt' and script_data['file_type'] in ['py', 'sh', 'bash']:
            try:
                os.chmod(file_path, 0o755)
            except:
                pass
        
        # 添加脚本记录到数据库
        script_id = Script.add(
            script_data['name'], 
            script_data['description'], 
            file_path, 
            script_data['file_type'],
            None  # url_path parameter
        )
        
        if script_id:
            script_ids.append(script_id)
            print(f"  创建脚本: {script_data['name']} (ID: {script_id})")
            
            # 添加脚本参数
            for param in script_data['parameters']:
                param_id = ScriptParameter.add(
                    script_id,
                    param['name'],
                    param['description'],
                    param['param_type'],
                    param['is_required'],
                    param['default_value']
                )
                if param_id:
                    print(f"    添加参数: {param['name']} (ID: {param_id})")
        else:
            print(f"  创建脚本失败: {script_data['name']}")
    
    return script_ids


def create_sample_chains(script_ids):
    """创建示例脚本链"""
    if not script_ids or len(script_ids) < 3:
        print("脚本数量不足，无法创建示例脚本链")
        return []
    
    print("正在创建示例脚本链...")
    
    # 获取脚本名称的映射关系
    script_names = {}
    for script_id in script_ids:
        script = Script.get(script_id)
        if script:
            script_names[script_id] = script['name']
    
    # 示例脚本链数据
    chains_data = [
        {
            "name": "系统信息收集与备份",
            "description": "收集系统信息并备份数据库",
            "nodes": [
                {"script_id": script_ids[0], "node_order": 1},  # 系统信息获取
                {"script_id": script_ids[3], "node_order": 2}   # 数据库备份
            ]
        },
        {
            "name": "文件生成与分析",
            "description": "生成临时日志文件并进行分析",
            "nodes": [
                {"script_id": script_ids[1], "node_order": 1},  # 文件生成器
                {"script_id": script_ids[2], "node_order": 2}   # 日志分析器
            ]
        },
        {
            "name": "完整诊断流程",
            "description": "执行完整的系统诊断流程，包括系统信息获取、网络诊断和数据库备份",
            "nodes": [
                {"script_id": script_ids[0], "node_order": 1},  # 系统信息获取
                {"script_id": script_ids[4], "node_order": 2},  # 网络诊断
                {"script_id": script_ids[3], "node_order": 3}   # 数据库备份
            ]
        }
    ]
    
    chain_ids = []
    for chain_data in chains_data:
        # 添加脚本链记录到数据库
        chain_id = ScriptChain.add(
            chain_data['name'],
            chain_data['description']
        )
        
        if chain_id:
            chain_ids.append(chain_id)
            print(f"  创建脚本链: {chain_data['name']} (ID: {chain_id})")
            
            # 添加脚本链节点
            for node in chain_data['nodes']:
                node_id = ChainNode.add(
                    chain_id,
                    node['script_id'],
                    node['node_order']
                )
                
                if node_id:
                    script_info = Script.get(node['script_id'])
                    script_name = script_info['name'] if script_info else "未知脚本"
                    print(f"    添加节点: {script_name} (顺序: {node['node_order']})")
        else:
            print(f"  创建脚本链失败: {chain_data['name']}")
    
    return chain_ids


def create_sample_executions(script_ids, chain_ids):
    """创建示例执行历史记录"""
    if not script_ids or not chain_ids:
        print("脚本或脚本链不存在，无法创建示例执行历史")
        return []
    
    print("正在创建示例执行历史记录...")
    
    # 生成一些随机的执行状态
    statuses = ['completed', 'failed', 'running']
    
    # 为脚本创建执行历史
    execution_ids = []
    
    # 创建一些成功的脚本执行
    for script_id in script_ids:
        # 每个脚本创建3-5条记录
        record_count = random.randint(3, 5)
        
        for i in range(record_count):
            # 随机选择状态，但大部分是成功的
            status = random.choices(
                statuses, 
                weights=[0.7, 0.2, 0.1], 
                k=1
            )[0]
            
            # 创建参数
            params = {}
            script = Script.get(script_id)
            
            if script:
                # 根据脚本参数生成随机参数值
                script_params = ScriptParameter.get_by_script(script_id)
                for param in script_params:
                    if param['param_type'] == 'string':
                        params[param['name']] = f"test_value_{random.randint(1, 100)}"
                    elif param['param_type'] == 'number':
                        params[param['name']] = random.randint(1, 100)
                    elif param['param_type'] == 'boolean':
                        params[param['name']] = random.choice([True, False])
                    elif param['param_type'] == 'json':
                        params[param['name']] = {"key": f"value_{random.randint(1, 100)}"}
            
            # 创建执行记录
            start_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # 随机生成输出
            output = None
            error = None
            
            if status == 'completed':
                output = json.dumps({
                    "result": "success",
                    "data": {
                        "processed_items": random.randint(10, 100),
                        "timestamp": start_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            elif status == 'failed':
                error = f"执行失败: 错误代码 {random.randint(1, 100)}, 原因: 测试错误"
            
            # 添加执行历史记录
            execution_id = ExecutionHistory.add(
                script_id=script_id,
                chain_id=None,
                status=status,
                params=params,
                output=output,
                error=error
            )
            
            if execution_id:
                execution_ids.append(execution_id)
                
                # 如果状态是已完成或失败，更新结束时间
                if status in ['completed', 'failed']:
                    # 随机生成执行时间（秒）
                    execution_time = random.uniform(0.5, 60)
                    end_time = start_time + datetime.timedelta(seconds=execution_time)
                    
                    # 更新数据库中的开始时间
                    conn = DBManager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        "UPDATE execution_history SET start_time = ? WHERE id = ?",
                        (start_time.strftime('%Y-%m-%d %H:%M:%S'), execution_id)
                    )
                    
                    conn.commit()
                    
                    # 更新结束时间和执行时间
                    cursor.execute(
                        "UPDATE execution_history SET end_time = ?, execution_time = ? WHERE id = ?",
                        (end_time.strftime('%Y-%m-%d %H:%M:%S'), execution_time, execution_id)
                    )
                    
                    conn.commit()
                    conn.close()
                
                print(f"  创建脚本执行记录: ID {execution_id}, 状态: {status}")
    
    # 为脚本链创建执行历史
    for chain_id in chain_ids:
        # 每个脚本链创建2-4条记录
        record_count = random.randint(2, 4)
        
        for i in range(record_count):
            # 随机选择状态，但大部分是成功的
            status = random.choices(
                statuses, 
                weights=[0.7, 0.2, 0.1], 
                k=1
            )[0]
            
            # 创建执行记录
            start_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # 随机生成输出
            output = None
            error = None
            
            if status == 'completed':
                output = json.dumps({
                    "result": "success",
                    "chain_execution": {
                        "total_nodes": random.randint(2, 5),
                        "completed_nodes": random.randint(2, 5),
                        "timestamp": start_time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            elif status == 'failed':
                error = f"执行失败: 脚本链执行中断，节点 {random.randint(1, 3)} 失败"
            
            # 添加执行历史记录
            execution_id = ExecutionHistory.add(
                script_id=None,
                chain_id=chain_id,
                status=status,
                params=None,
                output=output,
                error=error
            )
            
            if execution_id:
                execution_ids.append(execution_id)
                
                # 如果状态是已完成或失败，更新结束时间
                if status in ['completed', 'failed']:
                    # 随机生成执行时间（秒）
                    execution_time = random.uniform(1, 120)
                    end_time = start_time + datetime.timedelta(seconds=execution_time)
                    
                    # 更新数据库中的开始时间
                    conn = DBManager.get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        "UPDATE execution_history SET start_time = ? WHERE id = ?",
                        (start_time.strftime('%Y-%m-%d %H:%M:%S'), execution_id)
                    )
                    
                    conn.commit()
                    
                    # 更新结束时间和执行时间
                    cursor.execute(
                        "UPDATE execution_history SET end_time = ?, execution_time = ? WHERE id = ?",
                        (end_time.strftime('%Y-%m-%d %H:%M:%S'), execution_time, execution_id)
                    )
                    
                    conn.commit()
                    conn.close()
                
                print(f"  创建脚本链执行记录: ID {execution_id}, 状态: {status}")
    
    return execution_ids


def create_sample_alert_configs():
    """创建示例告警配置"""
    print("正在创建示例告警配置...")
    
    # 示例告警配置数据
    alert_configs_data = [
        {
            "name": "脚本执行失败告警",
            "description": "当脚本执行失败时触发告警",
            "alert_type": "execution_status",
            "condition_type": "equals",
            "condition_value": "failed",
            "notification_type": "email",
            "notification_config": {
                "recipients": ["zhuyuanhui2002@163.com"]
            }
        },
        {
            "name": "执行时间过长告警",
            "description": "当脚本执行时间超过30秒时触发告警",
            "alert_type": "execution_time",
            "condition_type": "greater_than",
            "condition_value": "30",
            "notification_type": "email",
            "notification_config": {
                "recipients": ["zhuyuanhui2002@163.com"]
            }
        },
        {
            "name": "脚本链执行失败告警",
            "description": "当脚本链执行失败时触发告警",
            "alert_type": "execution_status",
            "condition_type": "equals",
            "condition_value": "failed",
            "notification_type": "email",
            "notification_config": {
                "recipients": ["zhuyuanhui2002@163.com"]
            }
        }
    ]
    
    alert_config_ids = []
    for config_data in alert_configs_data:
        # 添加告警配置记录到数据库
        config_id = AlertConfig.add(
            config_data['name'],
            config_data['description'],
            config_data['alert_type'],
            config_data['condition_type'],
            config_data['condition_value'],
            config_data['notification_type'],
            config_data['notification_config']
        )
        
        if config_id:
            alert_config_ids.append(config_id)
            print(f"  创建告警配置: {config_data['name']} (ID: {config_id})")
        else:
            print(f"  创建告警配置失败: {config_data['name']}")
    
    return alert_config_ids


def create_sample_alert_history(alert_config_ids, execution_ids):
    """创建示例告警历史记录"""
    if not alert_config_ids or not execution_ids:
        print("告警配置或执行历史不存在，无法创建示例告警历史")
        return []
    
    print("正在创建示例告警历史记录...")
    
    # 筛选出状态为failed的执行记录
    conn = DBManager.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM execution_history WHERE status = 'failed' LIMIT 10"
    )
    
    failed_execution_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not failed_execution_ids:
        # 如果没有失败的执行记录，随机选择一些
        failed_execution_ids = random.sample(execution_ids, min(5, len(execution_ids)))
    
    # 创建告警历史记录
    alert_history_ids = []
    for execution_id in failed_execution_ids:
        # 随机选择一个告警配置
        alert_config_id = random.choice(alert_config_ids)
        
        # 创建告警历史记录
        alert_id = AlertHistory.add(
            alert_config_id,
            execution_id,
            random.choice(['sent', 'failed']),
            f"测试告警消息 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if alert_id:
            alert_history_ids.append(alert_id)
            print(f"  创建告警历史记录: ID {alert_id}, 执行ID: {execution_id}")
    
    return alert_history_ids


def create_sample_scheduled_tasks(script_ids, chain_ids):
    """创建示例定时任务"""
    if not script_ids and not chain_ids:
        print("脚本或脚本链不存在，无法创建示例定时任务")
        return []
    
    print("正在创建示例定时任务...")
    
    # 一些常用的cron表达式
    cron_expressions = [
        "0 0 * * *",       # 每天午夜执行
        "0 12 * * *",      # 每天中午执行
        "0 */6 * * *",     # 每6小时执行一次
        "0 0 * * 0",       # 每周日午夜执行
        "0 0 1 * *",       # 每月1号午夜执行
        "*/30 * * * *",    # 每30分钟执行一次
        "0 8-18 * * 1-5"   # 工作日上午8点到下午6点每小时执行一次
    ]
    
    # 示例定时任务数据
    tasks_data = []
    
    # 为脚本创建定时任务
    for script_id in script_ids[:3]:  # 只为前3个脚本创建
        script = Script.get(script_id)
        if not script:
            continue
        
        # 随机选择一个cron表达式
        cron = random.choice(cron_expressions)
        
        # 生成参数
        params = {}
        script_params = ScriptParameter.get_by_script(script_id)
        
        for param in script_params:
            if param['param_type'] == 'string':
                params[param['name']] = f"scheduled_value_{random.randint(1, 100)}"
            elif param['param_type'] == 'number':
                params[param['name']] = random.randint(1, 100)
            elif param['param_type'] == 'boolean':
                params[param['name']] = random.choice([True, False])
            elif param['param_type'] == 'json':
                params[param['name']] = {"key": f"value_{random.randint(1, 100)}"}
        
        tasks_data.append({
            "name": f"{script['name']}定时任务",
            "description": f"定时执行{script['name']}脚本",
            "script_id": script_id,
            "chain_id": None,
            "schedule_type": "cron",
            "cron_expression": cron,
            "params": params
        })
    
    # 为脚本链创建定时任务
    for chain_id in chain_ids:
        chain = ScriptChain.get(chain_id)
        if not chain:
            continue
        
        # 随机选择一个cron表达式
        cron = random.choice(cron_expressions)
        
        tasks_data.append({
            "name": f"{chain['name']}定时任务",
            "description": f"定时执行{chain['name']}脚本链",
            "script_id": None,
            "chain_id": chain_id,
            "schedule_type": "cron",
            "cron_expression": cron,
            "params": None
        })
    
    # 添加定时任务记录到数据库
    task_ids = []
    for task_data in tasks_data:
        task_id = ScheduledTask.add(
            task_data['name'],
            task_data['description'],
            task_data['schedule_type'],
            task_data['cron_expression'],
            task_data['script_id'],
            task_data['chain_id'],
            task_data['params']
        )
        
        if task_id:
            task_ids.append(task_id)
            print(f"  创建定时任务: {task_data['name']} (ID: {task_id})")
        else:
            print(f"  创建定时任务失败: {task_data['name']}")
    
    return task_ids


def main():
    """主函数"""
    print("开始填充示例数据...")
    
    # 初始化数据库
    initialize_db()
    
    # 创建示例脚本
    script_ids = create_sample_scripts()
    
    # 创建示例脚本链
    chain_ids = create_sample_chains(script_ids)
    
    # 创建示例执行历史记录
    execution_ids = create_sample_executions(script_ids, chain_ids)
    
    # 创建示例告警配置
    alert_config_ids = create_sample_alert_configs()
    
    # 创建示例告警历史记录
    alert_history_ids = create_sample_alert_history(alert_config_ids, execution_ids)
    
    # 创建示例定时任务
    task_ids = create_sample_scheduled_tasks(script_ids, chain_ids)
    
    print("\n示例数据填充完成！")
    print(f"- 创建了 {len(script_ids)} 个示例脚本")
    print(f"- 创建了 {len(chain_ids)} 个示例脚本链")
    print(f"- 创建了 {len(execution_ids)} 条示例执行历史记录")
    print(f"- 创建了 {len(alert_config_ids)} 个示例告警配置")
    print(f"- 创建了 {len(alert_history_ids)} 条示例告警历史记录")
    print(f"- 创建了 {len(task_ids)} 个示例定时任务")


if __name__ == "__main__":
    main()
