#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试统计数据API脚本
直接调用execution_history.get_statistics方法，并模拟API调用
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta

# 将项目根目录添加到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from backend.models.execution import ExecutionHistory

def test_get_statistics_method():
    """直接测试ExecutionHistory.get_statistics方法"""
    print("测试ExecutionHistory.get_statistics方法...")
    try:
        # 获取30天前的日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 格式化日期
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 调用get_statistics方法
        print(f"查询参数: period=day, start_date={start_date_str}, end_date={end_date_str}")
        statistics = ExecutionHistory.get_statistics(
            period='day',
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        # 打印结果
        print(f"获取到{len(statistics)}条统计数据")
        
        if statistics:
            print("\n统计数据示例:")
            for i, stat in enumerate(statistics[:3]):
                print(f"  第{i+1}条:")
                for key, value in stat.items():
                    print(f"    {key}: {value}")
        
        return True
    except Exception as e:
        print(f"测试ExecutionHistory.get_statistics方法失败: {str(e)}")
        return False

def test_api_endpoint():
    """测试统计数据API端点"""
    print("\n测试API端点...")
    try:
        # 获取30天前的日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # 格式化日期
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 构建请求参数
        params = {
            'period': 'day',
            'start_date': start_date_str,
            'end_date': end_date_str
        }
        
        # 发送API请求
        url = 'http://localhost:5000/api/execution/statistics'
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        
        response = requests.get(url, params=params)
        
        # 打印响应状态码
        print(f"响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            data = response.json()
            print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('code') == 0:
                stats = data.get('data', [])
                print(f"API返回{len(stats)}条统计数据")
            else:
                print(f"API返回错误: {data.get('message')}")
        except Exception as e:
            print(f"解析响应失败: {str(e)}")
            print(f"原始响应内容: {response.text}")
        
        # 模拟前端发送的请求
        print("\n模拟前端请求...")
        
        # 常见的前端请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        print(f"响应状态码: {response.status_code}")
        
        try:
            data = response.json()
            print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"解析响应失败: {str(e)}")
            print(f"原始响应内容: {response.text}")
        
        return True
    except Exception as e:
        print(f"测试API端点失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试统计数据API...")
    method_ok = test_get_statistics_method()
    api_ok = test_api_endpoint()
    
    if method_ok and api_ok:
        print("\n测试完成")
    else:
        print("\n测试过程中发现问题")
