# -*- coding: utf-8 -*-
"""
AI脚本生成模块
利用大模型API自动生成满足系统要求的脚本
"""
# 导入子模块
from .script_generator import ScriptGenerator
from .script_analyzer import ScriptAnalyzer
from .script_validator import ScriptValidator
from .parameter_extractor import ParameterExtractor

class AIGenerator:
    """AI脚本生成器类，提供对子模块功能的统一访问"""
    
    @staticmethod
    def generate_script(script_name, description, script_type, requirements, api_key=None, model="qwen-plus"):
        """
        使用大模型API生成脚本
        
        Args:
            script_name: 脚本名称
            description: 脚本描述
            script_type: 脚本类型 (py, js, sh, ps1, bat)
            requirements: 脚本需求描述
            api_key: API密钥
            model: 使用的模型名称
            
        Returns:
            tuple: (success, script_content, error)
        """
        return ScriptGenerator.generate_script(
            script_name, description, script_type, requirements, api_key, model
        )
    
    @staticmethod
    def save_generated_script(script_name, description, script_type, script_content, url_path=None):
        """
        保存生成的脚本到文件系统和数据库
        
        Args:
            script_name: 脚本名称
            description: 脚本描述
            script_type: 脚本类型 (py, js, sh, ps1, bat)
            script_content: 脚本内容
            url_path: URL路径(可选)
            
        Returns:
            tuple: (success, script_id, file_path, error)
        """
        return ScriptGenerator.save_generated_script(
            script_name, description, script_type, script_content, url_path
        )
    
    @staticmethod
    def extract_and_save_parameters(script_id, script_content, script_type):
        """
        提取脚本中的参数并保存到数据库
        
        Args:
            script_id: 脚本ID
            script_content: 脚本内容
            script_type: 脚本类型
            
        Returns:
            bool: 是否成功
        """
        return ParameterExtractor.extract_and_save_parameters(
            script_id, script_content, script_type
        )
    
    @staticmethod
    def extract_params_via_api(script_content, script_type, api_key=None):
        """
        通过API提取脚本中的参数
        
        Args:
            script_content: 脚本内容
            script_type: 脚本类型
            api_key: API密钥
            
        Returns:
            list: 参数列表
        """
        return ParameterExtractor.extract_params_via_api(
            script_content, script_type, api_key
        )

    @staticmethod
    def analyze_script(script_id, analysis_type='general', api_key=None, model="qwen-plus"):
        """
        使用大模型分析脚本并提供改进建议
        
        Args:
            script_id: 脚本ID
            analysis_type: 分析类型，可选值：general(一般分析), performance(性能分析), security(安全分析), 
                           readability(可读性分析), best_practices(最佳实践)
            api_key: API密钥
            model: 使用的模型名称
            
        Returns:
            tuple: (success, analysis_result, error)
        """
        return ScriptAnalyzer.analyze_script(
            script_id, analysis_type, api_key, model
        )

    @staticmethod
    def generate_script_from_template(template_language, template_has_params, template_output_mode, 
                                      script_name, description, requirements, api_key=None, model="qwen-plus"):
        """
        基于系统模板使用大模型生成脚本
        
        Args:
            template_language: 模板语言，可选值：python, shell, batch, powershell, js
            template_has_params: 是否带参数
            template_output_mode: 输出模式，可选值：json, file, none
            script_name: 脚本名称
            description: 脚本描述
            requirements: 具体功能要求
            api_key: API密钥
            model: 使用的模型名称
            
        Returns:
            tuple: (success, script_content, error)
        """
        return ScriptGenerator.generate_script_from_template(
            template_language, template_has_params, template_output_mode,
            script_name, description, requirements, api_key, model
        )

    @staticmethod
    def validate_script(script_content, script_type, requirements, api_key=None, model="qwen-plus"):
        """
        验证生成的脚本是否满足要求
        
        Args:
            script_content: 脚本内容
            script_type: 脚本类型
            requirements: 脚本需求描述
            api_key: API密钥
            model: 使用的模型名称
            
        Returns:
            tuple: (success, validation_result, error)
        """
        return ScriptValidator.validate_script(
            script_content, script_type, requirements, api_key, model
        )

# 导出所有类
__all__ = [
    'AIGenerator',
    'ScriptGenerator',
    'ScriptAnalyzer',
    'ScriptValidator',
    'ParameterExtractor'
]
