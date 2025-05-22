# -*- coding: utf-8 -*-
"""
脚本分析器模块
利用大模型API分析脚本并提供改进建议
"""
import os
from openai import OpenAI
from models.script import Script
from models.script.script_version import ScriptVersion
from config import logger, AI_API_KEY

class ScriptAnalyzer:
    """脚本分析器类，提供脚本分析功能"""
    
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
        try:
            # 使用提供的API密钥或默认密钥
            api_key = api_key or AI_API_KEY
            
            if not api_key:
                return False, None, "未配置AI API密钥"
            
            # 获取脚本信息
            script = Script.get(script_id)
            if not script:
                return False, None, f"未找到脚本(ID:{script_id})"
            
            # 获取脚本最新版本内容
            latest_version = ScriptVersion.get_latest_version(script_id)
            if not latest_version:
                return False, None, f"脚本(ID:{script_id})没有版本记录"
            
            script_content = None
            
            # 检查是否存在file_path字段并尝试从文件读取内容
            file_path = None
            if isinstance(latest_version, dict) and 'file_path' in latest_version:
                file_path = latest_version.get('file_path')
            elif hasattr(latest_version, 'file_path'):
                file_path = latest_version.file_path
                
            # 如果存在file_path，尝试读取文件内容
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        script_content = file.read()
                    logger.info(f"已从文件路径读取脚本内容: {file_path}")
                except Exception as file_err:
                    logger.error(f"从文件读取脚本内容失败: {str(file_err)}，将使用数据库中的内容")
            
            # 如果从文件读取失败或没有file_path，从数据库获取内容
            if script_content is None:
                # 根据返回值的类型进行处理
                if isinstance(latest_version, dict):
                    script_content = latest_version.get('content')
                    if not script_content:
                        return False, None, f"脚本版本内容为空"
                else:
                    script_content = latest_version.content
            script_type = script["file_type"]
            script_name = script["name"]
            script_description = script["description"]
            
            # 构建分析提示
            analysis_prompts = {
                'general': f"""作为代码审查专家，请对以下{ScriptAnalyzer._get_language_name(script_type)}脚本进行全面分析，并提供改进建议：

脚本名称：{script_name}
脚本描述：{script_description}

```{script_type}
{script_content}
```

请从以下几个方面分析：
1. 代码质量：代码结构、命名规范、注释等
2. 功能实现：是否完整实现了描述的功能
3. 性能优化：是否有性能瓶颈或可以优化的地方
4. 安全性：是否存在安全隐患
5. 可读性：代码是否易于理解和维护
6. 最佳实践：是否遵循了该语言的最佳实践

请以Markdown格式提供分析结果，包括具体的改进建议和示例代码。""",
                
                'performance': f"""作为性能优化专家，请对以下{ScriptAnalyzer._get_language_name(script_type)}脚本进行性能分析，并提供优化建议：

脚本名称：{script_name}
脚本描述：{script_description}

```{script_type}
{script_content}
```

请从以下几个方面分析性能：
1. 算法复杂度：是否使用了高效的算法
2. 资源使用：内存使用、I/O 操作优化
3. 计算密集型操作：是否可以优化计算方式
4. 数据结构选择：是否使用了合适的数据结构
5. 循环和迭代：是否可以优化循环结构
6. 并发处理：是否可以通过并发提高性能

请以Markdown格式提供分析结果，包括具体的优化建议和示例代码。""",
                
                'security': f"""作为安全专家，请对以下{ScriptAnalyzer._get_language_name(script_type)}脚本进行安全性分析，并提供加固建议：

脚本名称：{script_name}
脚本描述：{script_description}

```{script_type}
{script_content}
```

请从以下几个方面分析安全性：
1. 输入验证：是否对所有输入进行了验证
2. 敏感信息处理：是否安全处理了敏感信息
3. 文件操作安全：是否存在路径遍历等风险
4. 命令注入：是否存在命令注入风险
5. 错误处理：是否泄露了敏感信息
6. 权限控制：是否有适当的权限控制

请以Markdown格式提供分析结果，包括具体的安全加固建议和示例代码。""",
                
                'readability': f"""作为代码可读性专家，请对以下{ScriptAnalyzer._get_language_name(script_type)}脚本进行可读性分析，并提供改进建议：

脚本名称：{script_name}
脚本描述：{script_description}

```{script_type}
{script_content}
```

请从以下几个方面分析可读性：
1. 命名规范：变量、函数、类的命名是否清晰
2. 代码格式：缩进、空行、代码布局等
3. 注释质量：注释是否有助于理解代码
4. 函数长度：函数是否过长或过于复杂
5. 代码复杂度：代码是否过于复杂难以理解
6. 模块化：代码是否适当拆分为模块和函数

请以Markdown格式提供分析结果，包括具体的改进建议和示例代码。""",
                
                'best_practices': f"""作为{ScriptAnalyzer._get_language_name(script_type)}专家，请对以下脚本进行最佳实践分析，并提供改进建议：

脚本名称：{script_name}
脚本描述：{script_description}

```{script_type}
{script_content}
```

请从以下几个方面分析是否遵循最佳实践：
1. 语言规范：是否遵循该语言的推荐规范
2. 设计模式：是否使用了合适的设计模式
3. 错误处理：是否正确处理了可能的错误
4. 代码组织：代码结构是否符合最佳实践
5. 依赖管理：是否正确管理了依赖
6. 测试性：代码是否易于测试

请以Markdown格式提供分析结果，包括具体的改进建议和示例代码。"""
            }
            
            # 使用选定的分析类型，默认为general
            prompt = analysis_prompts.get(analysis_type, analysis_prompts['general'])
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            
            try:
                # 调用API分析脚本
                completion = client.chat.completions.create(
                    model=model, 
                    messages=[
                        {"role": "system", "content": "You are a code review expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 获取分析结果
                analysis_result = completion.choices[0].message.content
                
                if not analysis_result:
                    return False, None, "API返回的分析结果为空"
                
                return True, analysis_result, None
                
            except Exception as api_error:
                return False, None, f"API调用失败: {str(api_error)}"
            
        except Exception as e:
            logger.error(f"分析脚本时发生错误: {str(e)}")
            return False, None, f"分析脚本失败: {str(e)}"
    
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
