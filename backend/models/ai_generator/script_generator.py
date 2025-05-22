# -*- coding: utf-8 -*-
"""
脚本生成器模块
利用大模型API自动生成满足系统要求的脚本
"""
import os
import time
from openai import OpenAI
from datetime import datetime
from config import SCRIPT_DIR, DEFAULT_OUTPUT_MODE, logger, AI_API_KEY
from models.script.script_base import Script
from models.script.script_version import ScriptVersion
from utils.script_template_helper import ScriptTemplateHelper

class ScriptGenerator:
    """脚本生成器类，提供脚本生成和保存功能"""
    
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
        try:
            # 使用提供的API密钥或默认密钥
            api_key = api_key or AI_API_KEY
            
            if not api_key:
                return False, None, "未配置AI API密钥"
            
            # 构建提示信息
            prompt = f"""你是一个专业的脚本开发者，请根据以下需求生成一个{script_type}脚本：
            
脚本名称：{script_name}
脚本描述：{description}
脚本语言：{ScriptGenerator._get_language_name(script_type)}
功能需求：{requirements}

请确保生成的脚本满足以下条件：
1. 代码风格简洁、高效，遵循最佳实践
2. 包含适当的注释，解释关键功能和逻辑
3. 包含错误处理机制
4. 函数化设计，将功能模块化
5. 根据需求提供参数处理和输出

只需提供完整的代码，不需要解释说明。
"""
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            try:
                # 调用API生成脚本
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional script developer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 获取生成结果
                script_content = completion.choices[0].message.content
                
                if not script_content:
                    return False, None, "API返回的脚本内容为空"
                
                # 提取代码块（如果模型将代码包装在```中）
                if '```' in script_content:
                    # 提取第一个代码块
                    start_idx = script_content.find('```') + 3
                    end_idx = script_content.find('```', start_idx)
                    
                    # 跳过语言标识符（例如```python）
                    if script_content[start_idx:].startswith(script_type) or \
                       script_content[start_idx:].startswith(ScriptGenerator._get_language_name(script_type).lower()):
                        start_idx = script_content.find('\n', start_idx) + 1
                    
                    if start_idx < end_idx:
                        script_content = script_content[start_idx:end_idx].strip()
                
                return True, script_content, None
                
            except Exception as api_error:
                return False, None, f"API调用失败: {str(api_error)}"
            
        except Exception as e:
            logger.error(f"生成脚本时发生错误: {str(e)}")
            return False, None, f"生成脚本失败: {str(e)}"
    
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
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{script_name}.{script_type}"
            file_path = os.path.join(SCRIPT_DIR, filename)
            
            # 确保脚本目录存在
            os.makedirs(SCRIPT_DIR, exist_ok=True)
            
            # 保存脚本到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 创建脚本记录
            script = Script.create(
                name=script_name,
                description=description,
                script_type=script_type,
                file_path=file_path,
                url_path=url_path or '',
                output_mode=DEFAULT_OUTPUT_MODE,
                status=1  # 1表示正常状态
            )
            
            if not script:
                return False, None, None, "创建脚本记录失败"
            
            # 创建脚本版本记录
            version = ScriptVersion.create(
                script_id=script.id,
                version='1.0.0',
                content=script_content,
                changelog='初始版本（由AI生成）',
                status=1  # 1表示正常状态
            )
            
            if not version:
                return False, None, None, "创建脚本版本记录失败"
            
            return True, script.id, file_path, None
            
        except Exception as e:
            logger.error(f"保存生成的脚本时发生错误: {str(e)}")
            return False, None, None, f"保存脚本失败: {str(e)}"
    
    @staticmethod
    def generate_script_from_template(template_language, template_has_params, template_output_mode, 
                                      script_name, description, requirements, api_key=None, model="qwen-plus"):
        """
        基于系统模板使用大模型生成脚本
        
        Args:
            template_language: 模板语言，可选值：python, shell, javascript
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
        try:
            # 使用提供的API密钥或默认密钥
            api_key = api_key or AI_API_KEY
            
            if not api_key:
                return False, None, "未配置AI API密钥"
            
            # 获取模板文件路径
            template_path = ScriptTemplateHelper.get_template_path(template_language, template_has_params, template_output_mode)
            
            if not template_path or not os.path.exists(template_path):
                return False, None, f"未找到适用的模板文件: {template_language}/{template_has_params}/{template_output_mode}"
            
            # 读取模板内容
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 构建提示信息
            prompt = f"""你是一个专业的脚本开发者，请根据以下需求和模板生成一个{template_language}脚本：
            
脚本名称：{script_name}
脚本描述：{description}
功能需求：{requirements}

以下是模板代码，你需要在不破坏模板结构的情况下，填充功能实现代码：

```
{template_content}
```

请注意：
1. 保留模板中的所有注释和结构
2. 不要修改参数处理和输出模式的代码
3. 只实现功能部分的代码
4. 确保错误处理符合模板风格
5. 添加必要的注释说明你的实现

只需提供完整的代码，不需要解释说明。
"""
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            try:
                # 调用API生成脚本
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a professional script developer."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 获取生成结果
                script_content = completion.choices[0].message.content
                
                if not script_content:
                    return False, None, "API返回的脚本内容为空"
                
                # 提取代码块（如果模型将代码包装在```中）
                if '```' in script_content:
                    # 提取第一个代码块
                    start_idx = script_content.find('```') + 3
                    end_idx = script_content.find('```', start_idx)
                    
                    # 跳过语言标识符
                    if start_idx < len(script_content) and not script_content[start_idx].isalnum():
                        start_idx = script_content.find('\n', start_idx) + 1
                    
                    if start_idx < end_idx:
                        script_content = script_content[start_idx:end_idx].strip()
                
                # 映射模板语言到脚本类型
                script_type_map = {
                    'python': 'py',
                    'shell': 'sh',
                    'javascript': 'js'
                }
                script_type = script_type_map.get(template_language, 'py')
                
                return True, script_content, None
                
            except Exception as api_error:
                return False, None, f"API调用失败: {str(api_error)}"
            
        except Exception as e:
            logger.error(f"从模板生成脚本时发生错误: {str(e)}")
            return False, None, f"从模板生成脚本失败: {str(e)}"
    
    @staticmethod
    def _get_language_name(script_type):
        """根据脚本类型获取语言名称"""
        type_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'sh': 'Shell',
            'ps1': 'PowerShell',
            'bat': 'Batch'
        }
        return type_map.get(script_type, 'Unknown')
