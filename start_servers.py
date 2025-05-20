#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动前端和后端服务器
"""
import os
import sys
import subprocess
import threading
import time
import signal
import platform

def run_command(command, cwd=None):
    """运行命令并实时输出结果"""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        bufsize=1,
        universal_newlines=False
    )
    
    try:
        for raw_line in iter(process.stdout.readline, b''):
            try:
                # 尝试使用 UTF-8 解码
                line = raw_line.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # 如果 UTF-8 解码失败，尝试使用 GBK 解码
                    line = raw_line.decode('gbk')
                except UnicodeDecodeError:
                    # 如果 GBK 也解码失败，使用 latin-1（不会失败）
                    line = raw_line.decode('latin-1')
            
            print(line, end='')
    finally:
        process.stdout.close()
        
    return process.wait()

def start_backend():
    """启动后端服务器"""
    print("正在启动后端服务器...")
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    
    # Windows使用python直接执行，Linux/Mac使用python3
    python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
    command = f"{python_cmd} app.py"
    
    run_command(command, cwd=backend_dir)

def start_frontend():
    """启动前端服务器"""
    print("正在启动前端服务器...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    
    # 使用npm运行服务
    command = "npm run serve"
    
    run_command(command, cwd=frontend_dir)

def main():
    """主函数，启动两个服务器并处理中断信号"""
    try:
        # 创建线程并启动
        backend_thread = threading.Thread(target=start_backend)
        frontend_thread = threading.Thread(target=start_frontend)
        
        backend_thread.daemon = True
        frontend_thread.daemon = True
        
        print("启动服务器...")
        backend_thread.start()
        
        # 等待一段时间后再启动前端，确保后端已经就绪
        time.sleep(5)
        frontend_thread.start()
        
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在关闭服务器...")
        sys.exit(0)

if __name__ == "__main__":
    main()
