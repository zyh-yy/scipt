# -*- coding: utf-8 -*-
"""
脚本模板助手
提供脚本模板相关的功能
"""
import os
import sys
import json
from pathlib import Path

# 导入项目配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger

class ScriptTemplateHelper:
    """脚本模板助手类"""
    
    # 模板文件目录
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'scripts')
    
    # 支持的脚本语言和对应的文件扩展名
    LANGUAGES = {
        'python': 'py',
        'shell': 'sh',
        'batch': 'bat',
        'powershell': 'ps1',
        'js': 'js'
    }
    
    # 支持的输出模式
    OUTPUT_MODES = ['json', 'file', 'none']
    
    @staticmethod
    def get_template_path(language='python', has_params=True, output_mode='json'):
        """获取模板文件路径
        
        Args:
            language: 脚本语言，可选值：python, shell, batch, powershell, js
            has_params: 是否带参数
            output_mode: 输出模式，可选值：json, file, none
            
        Returns:
            str: 模板文件路径
        """
        # 验证参数
        if language not in ScriptTemplateHelper.LANGUAGES:
            logger.error(f"不支持的脚本语言: {language}")
            return None
        
        if output_mode not in ScriptTemplateHelper.OUTPUT_MODES:
            logger.error(f"不支持的输出模式: {output_mode}")
            return None
        
        # 构建模板文件名
        params_part = "with_params" if has_params else "without_params"
        template_name = f"{language}_{params_part}_{output_mode}.{ScriptTemplateHelper.LANGUAGES[language]}"
        template_path = os.path.join(ScriptTemplateHelper.TEMPLATE_DIR, template_name)
        
        # 检查模板文件是否存在
        if not os.path.exists(template_path):
            # 如果指定语言的模板不存在，尝试使用 Python 模板作为备选
            if language != 'python':
                fallback_name = f"python_{params_part}_{output_mode}.py"
                fallback_path = os.path.join(ScriptTemplateHelper.TEMPLATE_DIR, fallback_name)
                if os.path.exists(fallback_path):
                    logger.warning(f"模板 {template_name} 不存在，使用备选模板 {fallback_name}")
                    return fallback_path
            
            logger.error(f"模板文件不存在: {template_path}")
            return None
        
        return template_path
    
    @staticmethod
    def get_template_content(language='python', has_params=True, output_mode='json'):
        """获取模板文件内容
        
        Args:
            language: 脚本语言，可选值：python, shell, batch, powershell, js
            has_params: 是否带参数
            output_mode: 输出模式，可选值：json, file, none
            
        Returns:
            str: 模板文件内容
        """
        template_path = ScriptTemplateHelper.get_template_path(language, has_params, output_mode)
        if template_path is None:
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取模板文件失败: {str(e)}")
            return None
    
    @staticmethod
    def get_extension(language):
        """获取语言对应的文件扩展名
        
        Args:
            language: 脚本语言
            
        Returns:
            str: 文件扩展名
        """
        return ScriptTemplateHelper.LANGUAGES.get(language, 'py')
    
    @staticmethod
    def get_language_from_extension(extension):
        """根据文件扩展名获取语言
        
        Args:
            extension: 文件扩展名（不含点号）
            
        Returns:
            str: 语言名称
        """
        # 反向查找
        for lang, ext in ScriptTemplateHelper.LANGUAGES.items():
            if ext == extension:
                return lang
        
        return 'python'  # 默认为 Python
