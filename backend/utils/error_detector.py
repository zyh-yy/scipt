# -*- coding: utf-8 -*-
"""
错误检测工具
用于检测和分析脚本执行过程中的错误
"""
import os
import sys
import re
import json
import traceback
from datetime import datetime

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger

class ErrorDetector:
    """错误检测类"""
    
    # 错误类型定义
    ERROR_TYPES = {
        'syntax': '语法错误',
        'import': '导入错误',
        'name': '名称错误',
        'attribute': '属性错误',
        'type': '类型错误',
        'value': '值错误',
        'index': '索引错误',
        'key': '键错误',
        'zero_division': '除零错误',
        'permission': '权限错误',
        'file_not_found': '文件未找到',
        'io': '输入/输出错误',
        'timeout': '超时错误',
        'memory': '内存错误',
        'runtime': '运行时错误',
        'other': '其他错误'
    }
    
    @staticmethod
    def detect_error_type(error_text):
        """
        检测错误类型
        
        Args:
            error_text: 错误文本

        Returns:
            错误类型和描述的字典
        """
        error_patterns = {
            'syntax': r'SyntaxError',
            'import': r'ImportError|ModuleNotFoundError',
            'name': r'NameError',
            'attribute': r'AttributeError',
            'type': r'TypeError',
            'value': r'ValueError',
            'index': r'IndexError',
            'key': r'KeyError',
            'zero_division': r'ZeroDivisionError',
            'permission': r'PermissionError',
            'file_not_found': r'FileNotFoundError',
            'io': r'IOError',
            'timeout': r'TimeoutError',
            'memory': r'MemoryError',
            'runtime': r'RuntimeError'
        }
        
        for error_type, pattern in error_patterns.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                return {
                    'type': error_type,
                    'description': ErrorDetector.ERROR_TYPES.get(error_type, '未知错误')
                }
        
        return {
            'type': 'other',
            'description': ErrorDetector.ERROR_TYPES.get('other', '未知错误')
        }
    
    @staticmethod
    def parse_traceback(tb_text):
        """
        解析异常回溯信息
        
        Args:
            tb_text: 异常回溯文本

        Returns:
            错误定位信息的字典
        """
        # 提取文件名、行号和错误信息
        file_pattern = r'File "([^"]+)", line (\d+)'
        line_matches = re.findall(file_pattern, tb_text)
        
        # 提取错误消息
        error_msg_pattern = r'(?:Error|Exception): (.+?)(?:\n|$)'
        error_msg_match = re.search(error_msg_pattern, tb_text)
        error_msg = error_msg_match.group(1) if error_msg_match else "未知错误"
        
        # 构建错误定位信息
        locations = []
        for file_path, line_number in line_matches:
            locations.append({
                'file': os.path.basename(file_path),
                'full_path': file_path,
                'line': int(line_number)
            })
        
        return {
            'locations': locations,
            'error_message': error_msg.strip()
        }
    
    @staticmethod
    def analyze_error(exception=None, traceback_text=None):
        """
        分析错误并生成错误报告
        
        Args:
            exception: 异常对象
            traceback_text: 异常回溯文本

        Returns:
            错误报告字典
        """
        # 获取异常回溯信息
        if exception and not traceback_text:
            traceback_text = ''.join(traceback.format_exception(
                type(exception), exception, exception.__traceback__))
        
        if not traceback_text:
            return {
                'success': False,
                'error_type': 'unknown',
                'description': '未提供错误信息',
                'locations': [],
                'error_message': '无法分析错误',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        # 提取错误类型
        error_info = ErrorDetector.detect_error_type(traceback_text)
        
        # 解析回溯信息
        location_info = ErrorDetector.parse_traceback(traceback_text)
        
        # 生成错误报告
        error_report = {
            'success': False,
            'error_type': error_info['type'],
            'description': error_info['description'],
            'locations': location_info['locations'],
            'error_message': location_info['error_message'],
            'traceback': traceback_text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return error_report
    
    @staticmethod
    def format_error_report(error_report, format_type='text'):
        """
        格式化错误报告
        
        Args:
            error_report: 错误报告字典
            format_type: 输出格式，可选 'text', 'json', 'html'

        Returns:
            格式化后的错误报告
        """
        if format_type == 'json':
            return json.dumps(error_report, ensure_ascii=False, indent=2)
        
        elif format_type == 'html':
            html = [
                '<div class="error-report">',
                f'<h3>错误类型: {error_report["description"]}</h3>',
                f'<p>错误消息: {error_report["error_message"]}</p>',
                '<h4>错误位置:</h4>',
                '<ul>'
            ]
            
            for loc in error_report['locations']:
                html.append(f'<li>文件: {loc["file"]}, 行号: {loc["line"]}</li>')
            
            html.extend([
                '</ul>',
                f'<pre>{error_report["traceback"]}</pre>',
                f'<p>时间: {error_report["timestamp"]}</p>',
                '</div>'
            ])
            
            return '\n'.join(html)
        
        else:  # text
            text = [
                f'错误类型: {error_report["description"]}',
                f'错误消息: {error_report["error_message"]}',
                '错误位置:'
            ]
            
            for loc in error_report['locations']:
                text.append(f'  - 文件: {loc["file"]}, 行号: {loc["line"]}')
            
            text.extend([
                '异常回溯:',
                error_report["traceback"],
                f'时间: {error_report["timestamp"]}'
            ])
            
            return '\n'.join(text)
