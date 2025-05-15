# -*- coding: utf-8 -*-
"""
AI脚本生成模块
利用大模型API自动生成满足系统要求的脚本
"""
import os
import json
import requests
import datetime
from config import logger
from .base import DBManager
from .script import Script, ScriptParameter

class AIGenerator:
    """AI脚本生成器类"""
    
    @staticmethod
    def generate_script(script_name, description, script_type, requirements, api_key=None, model="gpt-3.5-turbo"):
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
        try:
            # 获取API密钥（如果未提供则从配置获取）
            if not api_key:
                # 可以从数据库或环境变量中获取默认API密钥
                from config import AI_API_KEY
                api_key = AI_API_KEY
            
            if not api_key:
                return False, None, "未提供API密钥"
            
            # 提示词工程，构建系统和用户提示词
            system_prompt = (
                "你是一个专业的脚本生成助手。请根据用户的需求，生成符合要求的脚本。"
                "脚本必须是完整的、可直接运行的，包含必要的注释和参数处理功能。"
                "脚本需要支持从命令行参数读取JSON格式的参数文件路径，解析参数后执行相应功能，"
                "并将结果输出到标准输出。如果出现错误，应该将错误信息输出到标准错误。"
            )
            
            # 根据脚本类型添加特定要求
            file_ext = script_type.lower()
            if file_ext == 'py':
                system_prompt += (
                    "脚本应当使用Python 3编写，包含必要的导入语句，"
                    "使用argparse或sys模块处理命令行参数，"
                    "至少包含main函数和脚本入口(if __name__ == '__main__':)。"
                    "处理JSON参数文件，并支持'__prev_output'特殊参数，该参数包含上一个脚本的输出。"
                )
            elif file_ext == 'js':
                system_prompt += (
                    "脚本应当使用Node.js编写，包含必要的require语句，"
                    "使用process.argv处理命令行参数，"
                    "处理JSON参数文件，并支持'__prev_output'特殊参数，该参数包含上一个脚本的输出。"
                )
            elif file_ext in ['sh', 'bash']:
                system_prompt += (
                    "脚本应当使用Bash编写，包含#!/bin/bash头部，"
                    "使用$1接收参数文件路径，"
                    "使用jq或其他方式解析JSON参数，并支持'__prev_output'特殊参数，该参数包含上一个脚本的输出。"
                )
            elif file_ext == 'ps1':
                system_prompt += (
                    "脚本应当使用PowerShell编写，"
                    "使用param()块或$args接收参数文件路径，"
                    "使用ConvertFrom-Json解析JSON参数，并支持'__prev_output'特殊参数，该参数包含上一个脚本的输出。"
                )
            elif file_ext == 'bat':
                system_prompt += (
                    "脚本应当使用Windows批处理命令编写，"
                    "使用%1接收参数文件路径，"
                    "需要考虑如何解析JSON参数（可能需要借助其他工具），并支持'__prev_output'特殊参数，该参数包含上一个脚本的输出。"
                )
            
            user_prompt = (
                f"请为我生成一个{script_type}脚本，命名为 '{script_name}'。\n\n"
                f"功能描述：{description}\n\n"
                f"具体要求：{requirements}\n\n"
                "请生成完整可运行的代码，包含参数处理、错误处理和必要的注释。"
                "请包含以下参数处理功能：\n"
                "1. 从命令行读取JSON参数文件路径\n"
                "2. 解析JSON参数文件\n"
                "3. 支持'__prev_output'特殊参数，该参数可能包含上一个脚本的输出\n"
                "4. 将结果输出到标准输出，将错误信息输出到标准错误\n"
                "只需返回脚本的完整代码，不需要额外的解释。"
            )
            
            # 构建API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # 发送API请求
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API请求失败: 状态码 {response.status_code}, 响应: {response.text}"
                logger.error(error_msg)
                return False, None, error_msg
            
            # 处理API响应
            response_data = response.json()
            script_content = response_data["choices"][0]["message"]["content"].strip()
            
            # 处理代码块标记
            if script_content.startswith("```"):
                # 移除代码块标记
                lines = script_content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                script_content = "\n".join(lines)
            
            return True, script_content, None
            
        except Exception as e:
            error_msg = f"生成脚本失败: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
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
        try:
            # 确保脚本文件夹存在
            from config import UPLOAD_FOLDER
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            # 为文件名添加时间戳
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{timestamp}_{script_name}.{script_type}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 写入脚本内容到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 如果是Linux/Unix系统，给予执行权限
            if os.name != 'nt' and script_type in ['py', 'sh', 'bash']:
                try:
                    os.chmod(file_path, 0o755)
                except:
                    pass
            
            # 添加脚本记录到数据库
            script_id = Script.add(script_name, description, file_path, script_type, url_path)
            
            if not script_id:
                # 删除已创建的文件
                try:
                    os.remove(file_path)
                except:
                    pass
                
                return False, None, None, "添加脚本到数据库失败"
            
            # 尝试提取参数并保存
            AIGenerator.extract_and_save_parameters(script_id, script_content, script_type)
            
            return True, script_id, file_path, None
            
        except Exception as e:
            error_msg = f"保存生成的脚本失败: {str(e)}"
            logger.error(error_msg)
            return False, None, None, error_msg
    
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
        try:
            params = []
            
            # 根据脚本类型使用不同的方式提取参数
            if script_type == 'py':
                # 使用另一个API调用来提取参数
                params = AIGenerator.extract_params_via_api(script_content, script_type)
            elif script_type == 'js':
                # 使用另一个API调用来提取参数
                params = AIGenerator.extract_params_via_api(script_content, script_type)
            
            # 如果成功提取到参数，则保存到数据库
            if params and isinstance(params, list):
                for param in params:
                    if isinstance(param, dict) and 'name' in param:
                        name = param.get('name')
                        description = param.get('description', '')
                        param_type = param.get('type', 'string')
                        is_required = param.get('required', 0)
                        default_value = param.get('default', None)
                        
                        ScriptParameter.add(
                            script_id, 
                            name, 
                            description, 
                            param_type, 
                            is_required, 
                            default_value
                        )
            
            return True
            
        except Exception as e:
            logger.error(f"提取和保存参数失败: {str(e)}")
            return False
    
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
        try:
            # 获取API密钥（如果未提供则从配置获取）
            if not api_key:
                # 可以从数据库或环境变量中获取默认API密钥
                from config import AI_API_KEY
                api_key = AI_API_KEY
            
            if not api_key:
                return []
            
            # 构建系统和用户提示词
            system_prompt = (
                "你是一个专业的脚本分析助手。请分析提供的脚本，提取其中处理的所有参数信息，"
                "包括参数名称、参数描述、参数类型、是否必填以及默认值。"
                "请以JSON格式返回结果，格式为参数列表: ["
                "  { \"name\": \"param_name\", \"description\": \"描述\", \"type\": \"string/number/boolean\", \"required\": 1或0, \"default\": \"默认值\" }"
                "]"
            )
            
            user_prompt = f"请分析以下{script_type}脚本，提取其中的参数信息，并以JSON格式返回：\n\n```\n{script_content}\n```"
            
            # 构建API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            # 发送API请求
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"参数提取API请求失败: 状态码 {response.status_code}, 响应: {response.text}")
                return []
            
            # 处理API响应
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"].strip()
            
            # 尝试解析返回的JSON
            try:
                # 提取JSON部分
                if "```json" in result:
                    json_part = result.split("```json")[1].split("```")[0].strip()
                elif "```" in result:
                    json_part = result.split("```")[1].strip()
                else:
                    json_part = result
                
                params = json.loads(json_part)
                if isinstance(params, list):
                    return params
                else:
                    return []
                    
            except Exception as e:
                logger.error(f"解析参数JSON失败: {str(e)}, 原始内容: {result}")
                return []
            
        except Exception as e:
            logger.error(f"通过API提取参数失败: {str(e)}")
            return []
