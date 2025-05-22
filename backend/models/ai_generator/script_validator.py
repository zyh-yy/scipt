# -*- coding: utf-8 -*-
"""
脚本验证器模块
利用大模型API验证脚本是否满足要求
"""
import os
from openai import OpenAI
from config import logger, AI_API_KEY

class ScriptValidator:
    """脚本验证器类，提供脚本验证功能"""
    
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
        try:
            # 使用提供的API密钥或默认密钥
            api_key = api_key or AI_API_KEY
            
            if not api_key:
                return False, None, "未配置AI API密钥"
            
            # 构建验证提示
            prompt = f"""作为代码审查专家，请验证以下{ScriptValidator._get_language_name(script_type)}脚本是否满足给定的需求：

脚本需求：
{requirements}

脚本内容：
```{script_type}
{script_content}
```

请验证脚本是否满足以下条件：
1. 功能完整性：是否完整实现了需求中描述的所有功能
2. 代码质量：代码结构、命名规范、注释等是否符合标准
3. 错误处理：是否包含适当的错误处理机制
4. 安全性：是否存在安全隐患
5. 可用性：脚本是否可以正常运行

请以Markdown格式提供验证结果，包括：
- 总体评价（是否通过验证）
- 功能完整性评价
- 代码质量评价
- 错误处理评价
- 安全性评价
- 可用性评价
- 改进建议（如果有）

请确保您的评价是客观、全面的。"""
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            try:
                # 调用API验证脚本
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a code review expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 获取验证结果
                validation_result = completion.choices[0].message.content
                
                if not validation_result:
                    return False, None, "API返回的验证结果为空"
                
                return True, validation_result, None
                
            except Exception as api_error:
                return False, None, f"API调用失败: {str(api_error)}"
            
        except Exception as e:
            logger.error(f"验证脚本时发生错误: {str(e)}")
            return False, None, f"验证脚本失败: {str(e)}"
    
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
