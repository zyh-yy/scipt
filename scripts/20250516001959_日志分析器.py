#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志分析脚本
分析日志文件并生成统计报告
"""
import os
import sys
import json
import re
import datetime
from collections import Counter

def analyze_log_file(file_path, pattern=None, time_window=None):
    """分析日志文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"日志文件不存在: {file_path}")
    
    # 设置默认正则表达式匹配ERROR, WARNING, INFO等级
    if not pattern:
        pattern = r'\[(ERROR|WARNING|INFO|DEBUG)\]'
    
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
        time_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
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
