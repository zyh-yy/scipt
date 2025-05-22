#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
超时测试脚本
用于测试系统处理长时间运行脚本的能力和超时机制
"""
import sys
import json
import time
import datetime
import random
import threading
import signal

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
    
    # 获取运行模式和超时时间
    run_mode = params.get("run_mode", "normal")
    sleep_seconds = params.get("sleep_seconds", 30)
    progress_interval = params.get("progress_interval", 5)
    
    # 输出开始执行信息
    start_info = {
        "script_type": "超时测试",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "run_mode": run_mode,
        "sleep_seconds": sleep_seconds,
        "progress_interval": progress_interval,
        "params_received": params
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 根据运行模式执行不同的测试
    if run_mode == "normal":
        result = run_normal_test(sleep_seconds, progress_interval)
    elif run_mode == "cpu_intensive":
        result = run_cpu_intensive_test(sleep_seconds, progress_interval)
    elif run_mode == "memory_intensive":
        result = run_memory_intensive_test(sleep_seconds, progress_interval)
    elif run_mode == "io_intensive":
        result = run_io_intensive_test(sleep_seconds, progress_interval)
    elif run_mode == "parallel":
        result = run_parallel_test(sleep_seconds, progress_interval)
    else:
        return_error(f"不支持的运行模式: {run_mode}")
        return 1
    
    # 如果测试失败，返回错误
    if not result["success"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    
    # 输出完成信息
    result["script_type"] = "超时测试"
    result["status"] = "完成"
    result["execution_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["total_run_time"] = result.get("total_run_time", sleep_seconds)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

def return_error(message):
    """输出错误信息并返回"""
    error = {
        "script_type": "超时测试",
        "status": "失败",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "error": message
    }
    print(json.dumps(error, ensure_ascii=False, indent=2))

def show_progress(current, total, interval):
    """显示进度信息"""
    if current % interval == 0 or current == total:
        progress = {
            "status": "进行中",
            "progress": {
                "current": current,
                "total": total,
                "percent": round(current / total * 100, 2) if total > 0 else 0
            },
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # 输出进度
        print(json.dumps(progress, ensure_ascii=False))

def run_normal_test(sleep_seconds, progress_interval):
    """正常超时测试，简单睡眠"""
    try:
        start_time = time.time()
        
        # 分段睡眠，每次间隔显示进度
        for i in range(1, sleep_seconds + 1):
            time.sleep(1)
            show_progress(i, sleep_seconds, progress_interval)
        
        end_time = time.time()
        run_time = end_time - start_time
        
        return {
            "success": True,
            "run_mode": "normal",
            "expected_time": sleep_seconds,
            "actual_time": round(run_time, 2),
            "message": "正常超时测试完成"
        }
    except Exception as e:
        return {
            "success": False,
            "run_mode": "normal",
            "error": str(e)
        }

def run_cpu_intensive_test(sleep_seconds, progress_interval):
    """CPU密集型超时测试，进行大量计算"""
    try:
        start_time = time.time()
        end_time = start_time + sleep_seconds
        
        iteration = 0
        progress_time = start_time
        
        # 进行密集计算直到达到超时时间
        while time.time() < end_time:
            # 执行一些CPU密集型计算
            result = 0
            for i in range(1000000):
                result += i % 7 * (i // 13)
            
            iteration += 1
            
            # 检查进度
            current_time = time.time()
            elapsed = current_time - start_time
            total = sleep_seconds
            
            # 每隔progress_interval秒显示一次进度
            if current_time - progress_time >= progress_interval:
                show_progress(min(int(elapsed), sleep_seconds), sleep_seconds, progress_interval)
                progress_time = current_time
        
        run_time = time.time() - start_time
        
        return {
            "success": True,
            "run_mode": "cpu_intensive",
            "expected_time": sleep_seconds,
            "actual_time": round(run_time, 2),
            "iterations": iteration,
            "message": "CPU密集型超时测试完成"
        }
    except Exception as e:
        return {
            "success": False,
            "run_mode": "cpu_intensive",
            "error": str(e)
        }

def run_memory_intensive_test(sleep_seconds, progress_interval):
    """内存密集型超时测试，分配大量内存"""
    try:
        start_time = time.time()
        end_time = start_time + sleep_seconds
        
        # 存储分配的内存列表
        memory_blocks = []
        block_size_mb = 10  # 每个内存块的大小（MB）
        max_blocks = 20     # 最大内存块数（限制总内存使用）
        
        iteration = 0
        progress_time = start_time
        
        # 循环分配和释放内存，直到达到超时时间
        while time.time() < end_time:
            # 分配内存（如果没有达到最大限制）
            if len(memory_blocks) < max_blocks:
                try:
                    # 分配一个新内存块
                    new_block = bytearray(block_size_mb * 1024 * 1024)
                    # 写入一些随机数据
                    for i in range(0, len(new_block), 1024):
                        new_block[i] = random.randint(0, 255)
                    
                    memory_blocks.append(new_block)
                except:
                    # 如果内存分配失败，跳过
                    pass
            
            # 如果已达到最大块数，随机释放一个，然后继续分配
            elif len(memory_blocks) > 0:
                index = random.randint(0, len(memory_blocks) - 1)
                memory_blocks.pop(index)
            
            # 每次循环短暂睡眠，避免CPU过载
            time.sleep(0.1)
            
            iteration += 1
            
            # 检查进度
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 每隔progress_interval秒显示一次进度
            if current_time - progress_time >= progress_interval:
                show_progress(min(int(elapsed), sleep_seconds), sleep_seconds, progress_interval)
                progress_time = current_time
        
        # 清理内存
        memory_blocks.clear()
        
        run_time = time.time() - start_time
        
        return {
            "success": True,
            "run_mode": "memory_intensive",
            "expected_time": sleep_seconds,
            "actual_time": round(run_time, 2),
            "max_memory_blocks": max_blocks,
            "block_size_mb": block_size_mb,
            "total_memory_mb": len(memory_blocks) * block_size_mb,
            "iterations": iteration,
            "message": "内存密集型超时测试完成"
        }
    except Exception as e:
        return {
            "success": False,
            "run_mode": "memory_intensive",
            "error": str(e)
        }

def run_io_intensive_test(sleep_seconds, progress_interval):
    """IO密集型超时测试，频繁读写文件"""
    import os
    import tempfile
    
    temp_files = []
    try:
        start_time = time.time()
        end_time = start_time + sleep_seconds
        
        file_count = 5      # 同时操作的文件数
        file_size_mb = 5    # 每个文件的大小（MB）
        
        # 创建临时文件
        for i in range(file_count):
            fd, path = tempfile.mkstemp(suffix=f'_test_{i}.dat')
            os.close(fd)
            temp_files.append(path)
        
        iteration = 0
        progress_time = start_time
        
        # 循环进行文件操作，直到达到超时时间
        while time.time() < end_time:
            # 选择一个随机文件
            file_index = iteration % file_count
            file_path = temp_files[file_index]
            
            # 写入数据
            with open(file_path, 'wb') as f:
                data = bytearray(file_size_mb * 1024 * 1024)
                for i in range(0, len(data), 4096):
                    for j in range(min(4096, len(data) - i)):
                        data[i + j] = random.randint(0, 255)
                f.write(data)
            
            # 读取数据
            with open(file_path, 'rb') as f:
                data = f.read()
            
            iteration += 1
            
            # 检查进度
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 每隔progress_interval秒显示一次进度
            if current_time - progress_time >= progress_interval:
                show_progress(min(int(elapsed), sleep_seconds), sleep_seconds, progress_interval)
                progress_time = current_time
        
        run_time = time.time() - start_time
        
        # 删除临时文件
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except:
                pass
        
        return {
            "success": True,
            "run_mode": "io_intensive",
            "expected_time": sleep_seconds,
            "actual_time": round(run_time, 2),
            "file_count": file_count,
            "file_size_mb": file_size_mb,
            "total_io_mb": iteration * file_size_mb,
            "iterations": iteration,
            "message": "IO密集型超时测试完成"
        }
    except Exception as e:
        # 删除临时文件
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except:
                pass
        
        return {
            "success": False,
            "run_mode": "io_intensive",
            "error": str(e)
        }

def run_parallel_test(sleep_seconds, progress_interval):
    """并行超时测试，创建多个线程执行任务"""
    try:
        start_time = time.time()
        end_time = start_time + sleep_seconds
        
        thread_count = 4    # 并行线程数
        threads = []
        thread_results = [{"iterations": 0} for _ in range(thread_count)]
        stop_flag = False
        
        # 定义线程函数
        def thread_func(thread_id, result_dict):
            nonlocal stop_flag
            iterations = 0
            
            # 线程执行直到达到超时时间或收到停止信号
            while not stop_flag:
                # 执行一些计算
                sum_val = 0
                for i in range(100000):
                    sum_val += i * (i % 5)
                
                iterations += 1
                result_dict["iterations"] = iterations
                
                # 短暂暂停
                time.sleep(0.01)
        
        # 创建并启动线程
        for i in range(thread_count):
            t = threading.Thread(target=thread_func, args=(i, thread_results[i]))
            t.daemon = True  # 设置为守护线程
            threads.append(t)
            t.start()
        
        # 主线程显示进度
        progress_time = start_time
        
        # 等待直到达到超时时间
        while time.time() < end_time:
            time.sleep(0.5)
            
            # 检查进度
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 每隔progress_interval秒显示一次进度
            if current_time - progress_time >= progress_interval:
                show_progress(min(int(elapsed), sleep_seconds), sleep_seconds, progress_interval)
                progress_time = current_time
        
        # 设置停止标志
        stop_flag = True
        
        # 等待所有线程结束
        for t in threads:
            t.join(timeout=1.0)
        
        run_time = time.time() - start_time
        
        # 汇总结果
        total_iterations = sum(r["iterations"] for r in thread_results)
        
        return {
            "success": True,
            "run_mode": "parallel",
            "expected_time": sleep_seconds,
            "actual_time": round(run_time, 2),
            "thread_count": thread_count,
            "iterations_per_thread": [r["iterations"] for r in thread_results],
            "total_iterations": total_iterations,
            "message": "并行超时测试完成"
        }
    except Exception as e:
        return {
            "success": False,
            "run_mode": "parallel",
            "error": str(e)
        }

if __name__ == "__main__":
    # 设置忽略SIGPIPE信号，避免在Docker中因管道断开而崩溃
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except:
        pass
    
    sys.exit(main())
