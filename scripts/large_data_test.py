#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大数据输出测试脚本
用于测试系统处理大量数据输出的能力
"""
import sys
import json
import os
import random
import string
import datetime
import time

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
    
    # 获取参数
    data_size_mb = params.get("data_size_mb", 1)  # 默认1MB
    output_mode = params.get("output_mode", "json")  # json, raw, file, stream
    complex_structure = params.get("complex_structure", False)  # 是否生成复杂结构
    output_file = params.get("output_file", "")  # 输出文件路径（当mode为file时使用）
    stream_delay_ms = params.get("stream_delay_ms", 100)  # 流式输出的延迟（毫秒）
    
    # 限制最大数据大小，避免系统问题
    max_size_mb = 50
    if data_size_mb > max_size_mb:
        print(json.dumps({
            "warning": f"指定的数据大小({data_size_mb}MB)超过限制，已调整为{max_size_mb}MB"
        }, ensure_ascii=False))
        data_size_mb = max_size_mb
    
    # 输出开始执行信息
    start_info = {
        "script_type": "大数据输出测试",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_size_mb": data_size_mb,
        "output_mode": output_mode,
        "complex_structure": complex_structure,
        "params_received": params
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 生成测试数据
    start_time = time.time()
    
    try:
        # 根据输出模式执行不同的测试
        if output_mode == "json":
            result = generate_json_output(data_size_mb, complex_structure)
        elif output_mode == "raw":
            result = generate_raw_output(data_size_mb)
        elif output_mode == "file":
            result = generate_file_output(data_size_mb, complex_structure, output_file)
        elif output_mode == "stream":
            result = generate_stream_output(data_size_mb, stream_delay_ms)
        else:
            print(json.dumps({
                "error": f"不支持的输出模式: {output_mode}"
            }, ensure_ascii=False))
            return 1
        
        # 如果测试失败，返回错误
        if not result["success"]:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 1
        
        # 计算总执行时间
        end_time = time.time()
        run_time = end_time - start_time
        
        # 输出完成信息
        result["script_type"] = "大数据输出测试"
        result["status"] = "完成"
        result["execution_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["run_time_seconds"] = round(run_time, 2)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        import traceback
        error_info = {
            "script_type": "大数据输出测试",
            "status": "失败",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }
        print(json.dumps(error_info, ensure_ascii=False, indent=2))
        return 1

def generate_random_string(length):
    """生成指定长度的随机字符串"""
    chars = string.ascii_letters + string.digits + '你好世界这是中文测试'
    return ''.join(random.choice(chars) for _ in range(length))

def generate_json_output(size_mb, complex_structure):
    """生成JSON格式的大数据输出"""
    result = {
        "success": True,
        "output_mode": "json",
        "data_size_mb": size_mb,
        "complex_structure": complex_structure
    }
    
    # 计算需要生成的数据量（估算值）
    if complex_structure:
        # 复杂结构：生成大量对象组成的数组
        items_count = int(size_mb * 100)  # 每个对象大约10KB
        items = []
        
        for i in range(items_count):
            # 生成不同大小的对象，使结构更复杂
            item = {
                "id": i,
                "name": f"Item-{i}",
                "description": generate_random_string(100),
                "details": {
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tags": [generate_random_string(10) for _ in range(5)],
                    "properties": {
                        "color": random.choice(["red", "green", "blue", "yellow"]),
                        "size": random.choice(["small", "medium", "large"]),
                        "weight": round(random.uniform(0.1, 100.0), 2),
                        "dimensions": {
                            "width": random.randint(1, 1000),
                            "height": random.randint(1, 1000),
                            "depth": random.randint(1, 1000)
                        }
                    },
                    "data": generate_random_string(200)
                }
            }
            items.append(item)
            
            # 定期检查大小，避免生成过多数据
            if i % 100 == 0:
                temp_result = {"items": items}
                json_size = len(json.dumps(temp_result, ensure_ascii=False).encode('utf-8'))
                if json_size >= size_mb * 1024 * 1024:
                    break
        
        result["items_count"] = len(items)
        result["items"] = items
    else:
        # 简单结构：主要是一个大字符串
        chars_count = int(size_mb * 1024 * 1024 / 4)  # 假设每个字符平均4字节（UTF-8编码）
        result["data"] = generate_random_string(chars_count)
    
    # 计算实际JSON大小
    json_data = json.dumps(result, ensure_ascii=False)
    actual_size = len(json_data.encode('utf-8'))
    result["actual_size_bytes"] = actual_size
    result["actual_size_mb"] = round(actual_size / (1024 * 1024), 2)
    
    return result

def generate_raw_output(size_mb):
    """生成原始文本格式的大数据输出"""
    # 计算字符数（估算值）
    chars_count = int(size_mb * 1024 * 1024 / 4)  # 假设每个字符平均4字节（UTF-8编码）
    
    # 生成随机文本
    start_time = time.time()
    data = generate_random_string(chars_count)
    generation_time = time.time() - start_time
    
    # 输出数据
    print(data)
    
    # 返回结果（不会输出，因为已经输出了原始数据）
    # 但这里仍然构建结果以便在调试时使用
    result = {
        "success": True,
        "output_mode": "raw",
        "data_size_mb": size_mb,
        "chars_count": chars_count,
        "generation_time_seconds": round(generation_time, 2),
        "actual_size_bytes": len(data.encode('utf-8')),
        "actual_size_mb": round(len(data.encode('utf-8')) / (1024 * 1024), 2)
    }
    
    return result

def generate_file_output(size_mb, complex_structure, output_file):
    """生成文件输出，将大数据写入指定文件"""
    result = {
        "success": True,
        "output_mode": "file",
        "data_size_mb": size_mb,
        "complex_structure": complex_structure
    }
    
    # 如果没有指定输出文件，创建临时文件
    if not output_file:
        import tempfile
        fd, output_file = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        result["output_file"] = output_file
        result["is_temp_file"] = True
    else:
        result["output_file"] = output_file
        result["is_temp_file"] = False
    
    # 生成数据并写入文件
    try:
        # 生成与JSON输出相同的数据结构
        if complex_structure:
            # 复杂结构
            data = {"items": []}
            items_count = int(size_mb * 100)  # 每个对象大约10KB
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # 写入开头
                f.write('{\n  "success": true,\n')
                f.write(f'  "output_mode": "file",\n')
                f.write(f'  "data_size_mb": {size_mb},\n')
                f.write(f'  "complex_structure": {str(complex_structure).lower()},\n')
                f.write('  "items": [\n')
                
                # 写入项目
                for i in range(items_count):
                    item = {
                        "id": i,
                        "name": f"Item-{i}",
                        "description": generate_random_string(100),
                        "details": {
                            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "tags": [generate_random_string(10) for _ in range(5)],
                            "properties": {
                                "color": random.choice(["red", "green", "blue", "yellow"]),
                                "size": random.choice(["small", "medium", "large"]),
                                "weight": round(random.uniform(0.1, 100.0), 2),
                                "dimensions": {
                                    "width": random.randint(1, 1000),
                                    "height": random.randint(1, 1000),
                                    "depth": random.randint(1, 1000)
                                }
                            },
                            "data": generate_random_string(200)
                        }
                    }
                    
                    # 写入项目，添加逗号（除了最后一项）
                    item_json = json.dumps(item, ensure_ascii=False, indent=4)
                    if i < items_count - 1:
                        f.write("    " + item_json + ",\n")
                    else:
                        f.write("    " + item_json + "\n")
                    
                    # 定期检查文件大小
                    if i % 100 == 0:
                        f.flush()
                        if os.path.getsize(output_file) >= size_mb * 1024 * 1024:
                            break
                
                # 写入结尾
                f.write('  ]\n}')
            
            # 获取实际项目数（如果提前结束循环）
            result["items_count"] = i + 1
            
        else:
            # 简单结构
            chars_count = int(size_mb * 1024 * 1024 / 4)  # 假设每个字符平均4字节（UTF-8编码）
            data = {
                "success": True,
                "output_mode": "file",
                "data_size_mb": size_mb,
                "complex_structure": complex_structure,
                "data": generate_random_string(chars_count)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 获取实际文件大小
        file_size = os.path.getsize(output_file)
        result["actual_size_bytes"] = file_size
        result["actual_size_mb"] = round(file_size / (1024 * 1024), 2)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "output_mode": "file",
            "error": str(e)
        }

def generate_stream_output(size_mb, delay_ms):
    """生成流式输出，逐步输出大量数据"""
    result = {
        "success": True,
        "output_mode": "stream",
        "data_size_mb": size_mb,
        "delay_ms": delay_ms
    }
    
    # 将大数据分成多个块输出
    chunk_size = 4096  # 每个块4KB
    total_chunks = int(size_mb * 1024 * 1024 / chunk_size)
    
    # 输出开始信息
    start_info = {
        "stream_start": True,
        "total_chunks": total_chunks,
        "chunk_size": chunk_size,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(json.dumps(start_info, ensure_ascii=False))
    sys.stdout.flush()
    
    # 逐块生成并输出数据
    actual_chunks = 0
    total_bytes = 0
    
    for i in range(total_chunks):
        # 生成随机数据
        chunk = generate_random_string(chunk_size)
        chunk_bytes = len(chunk.encode('utf-8'))
        total_bytes += chunk_bytes
        
        # 输出块信息
        chunk_info = {
            "chunk_number": i + 1,
            "chunk_bytes": chunk_bytes,
            "data": chunk
        }
        print(json.dumps(chunk_info, ensure_ascii=False))
        sys.stdout.flush()
        
        # 增加延迟
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        
        actual_chunks += 1
    
    # 输出结束信息
    end_info = {
        "stream_end": True,
        "chunks_sent": actual_chunks,
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / (1024 * 1024), 2),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(json.dumps(end_info, ensure_ascii=False))
    sys.stdout.flush()
    
    result["chunks_sent"] = actual_chunks
    result["total_bytes"] = total_bytes
    result["total_mb"] = round(total_bytes / (1024 * 1024), 2)
    
    return result

if __name__ == "__main__":
    sys.exit(main())
