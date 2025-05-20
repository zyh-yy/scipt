#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件生成脚本
根据指定的参数生成文件
"""
import os
import sys
import json
import random
import string
import datetime

def generate_random_string(length=10):
    """生成随机字符串"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_text_file(file_path, size_kb=10, content_type='random'):
    """生成文本文件"""
    # 创建目录（如果不存在）
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # 根据内容类型生成内容
    if content_type == 'random':
        content = generate_random_string(size_kb * 1024)
    elif content_type == 'timestamp':
        # 生成带时间戳的内容
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_content = f"Generated at {timestamp}\n"
        content = base_content
        while len(content) < size_kb * 1024:
            content += generate_random_string(100) + "\n"
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
