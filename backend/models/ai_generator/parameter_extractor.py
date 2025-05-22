# -*- coding: utf-8 -*-
"""
参数提取器模块
从脚本中提取参数信息并保存到数据库
"""
import re
import json
import requests
from models.script.script_parameter import ScriptParameter
from config import logger, AI_API_KEY

class ParameterExtractor:
    """参数提取器类，提供从脚本中提取参数的功能"""
    
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
            # 提取参数
            params = []
            
            # 根据脚本类型选择不同的提取方法
            if script_type == 'py':
                params = ParameterExtractor._extract_python_params(script_content)
            elif script_type == 'sh':
                params = ParameterExtractor._extract_shell_params(script_content)
            elif script_type == 'js':
                params = ParameterExtractor._extract_js_params(script_content)
            else:
                # 对于其他类型的脚本，使用AI提取
                success, ai_params, _ = ParameterExtractor.extract_params_via_api(script_content, script_type)
                if success and ai_params:
                    params = ai_params
            
            # 如果没有提取到参数，尝试使用AI提取
            if not params:
                success, ai_params, _ = ParameterExtractor.extract_params_via_api(script_content, script_type)
                if success and ai_params:
                    params = ai_params
            
            # 保存参数到数据库
            if params:
                # 先删除已存在的参数
                ScriptParameter.delete_by_script_id(script_id)
                
                # 保存新参数
                for param in params:
                    ScriptParameter.create(
                        script_id=script_id,
                        name=param.get('name', ''),
                        description=param.get('description', ''),
                        param_type=param.get('type', 'string'),
                        required=param.get('required', True),
                        default_value=param.get('default', ''),
                        position=param.get('position', 0)
                    )
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"提取和保存参数时发生错误: {str(e)}")
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
            tuple: (success, params, error)
        """
        try:
            # 使用提供的API密钥或默认密钥
            api_key = api_key or AI_API_KEY
            
            if not api_key:
                return False, None, "未配置AI API密钥"
            
            # 构建提示
            prompt = f"""作为代码分析专家，请分析以下{ParameterExtractor._get_language_name(script_type)}脚本，提取其中的参数信息：

```{script_type}
{script_content}
```

请提取脚本中的所有参数信息，并以以下JSON格式返回：

```json
[
  {{
    "name": "参数名称",
    "description": "参数描述",
    "type": "参数类型（string, number, boolean, array, object等）",
    "required": true/false,
    "default": "默认值（如果有）",
    "position": 参数位置（整数，从0开始）
  }},
  ...
]
```

请注意：
1. 只返回JSON格式的参数列表，不要包含其他解释文本
2. 如果脚本没有参数，返回空数组 []
3. 尽可能从脚本注释、帮助文档或参数处理代码中提取参数信息
4. 确保JSON格式正确，可以被解析

请直接返回JSON格式的参数列表，不要包含其他文本。"""
            
            # 调用API提取参数
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 构建请求参数
            payload = {
                "model": "qwen-plus",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # 发送请求到模型API
            response = requests.post(
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # 检查API响应
            if response.status_code != 200:
                return False, None, f"API请求失败，状态码: {response.status_code}, 响应: {response.text}"
            
            # 解析响应
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not content:
                return False, None, "API返回的内容为空"
            
            # 提取JSON内容
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析整个内容
                json_str = content
            
            # 解析JSON
            try:
                params = json.loads(json_str)
                if isinstance(params, list):
                    return True, params, None
                else:
                    return False, None, "API返回的参数格式不正确，应为数组"
            except json.JSONDecodeError as e:
                return False, None, f"解析参数JSON时发生错误: {str(e)}"
            
        except Exception as e:
            logger.error(f"通过API提取参数时发生错误: {str(e)}")
            return False, None, f"通过API提取参数失败: {str(e)}"
    
    @staticmethod
    def _extract_python_params(script_content):
        """提取Python脚本中的参数"""
        params = []
        position = 0
        
        # 查找argparse参数
        if 'argparse' in script_content:
            # 查找参数添加模式: add_argument
            pattern = r'add_argument\([\'"](-{1,2}[^\'",]+)[\'"](?:,\s*[\'"](-{1,2}[^\'",]+)[\'"])?(?:,\s*(?:dest|help|type|default|required|action)=([^,)]+))*'
            matches = re.finditer(pattern, script_content)
            
            for match in matches:
                param_name = match.group(1).lstrip('-')
                if match.group(2):  # 有短选项和长选项
                    if len(param_name) == 1:  # 短选项在前，长选项在后
                        param_name = match.group(2).lstrip('-')
                
                # 查找该参数的其他属性
                help_pattern = r'help=[\'"](.*?)[\'"]'
                help_match = re.search(help_pattern, match.group(0))
                description = help_match.group(1) if help_match else ''
                
                type_pattern = r'type=(\w+)'
                type_match = re.search(type_pattern, match.group(0))
                param_type = 'string'
                if type_match:
                    type_name = type_match.group(1)
                    if type_name in ('int', 'float'):
                        param_type = 'number'
                    elif type_name == 'bool':
                        param_type = 'boolean'
                
                required_pattern = r'required=(True|False)'
                required_match = re.search(required_pattern, match.group(0))
                required = True if required_match and required_match.group(1) == 'True' else False
                
                default_pattern = r'default=([^,)]+)'
                default_match = re.search(default_pattern, match.group(0))
                default_value = default_match.group(1) if default_match else ''
                if default_value and (default_value.startswith("'") or default_value.startswith('"')):
                    default_value = default_value[1:-1]  # 去除引号
                
                params.append({
                    'name': param_name,
                    'description': description,
                    'type': param_type,
                    'required': required,
                    'default': default_value,
                    'position': position
                })
                position += 1
        
        # 查找docstring中的参数说明
        docstring_pattern = r'"""(.*?)"""'
        docstring_match = re.search(docstring_pattern, script_content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1)
            param_pattern = r'(?:Args|Parameters):(.*?)(?:\n\s*(?:Returns|Raises|Yields|Examples|Notes)|$)'
            param_section_match = re.search(param_pattern, docstring, re.DOTALL)
            
            if param_section_match:
                param_section = param_section_match.group(1)
                param_lines = re.finditer(r'\s*(\w+)(?:\s*\(([^)]+)\))?\s*:\s*(.*?)(?=\n\s*\w+\s*(?:\([^)]+\))?\s*:|$)', param_section, re.DOTALL)
                
                for param_line in param_lines:
                    param_name = param_line.group(1)
                    param_type = param_line.group(2) or 'string'
                    description = param_line.group(3).strip()
                    
                    # 检查参数是否已存在
                    existing_param = next((p for p in params if p['name'] == param_name), None)
                    if existing_param:
                        # 更新现有参数
                        if not existing_param['description']:
                            existing_param['description'] = description
                        if existing_param['type'] == 'string' and param_type:
                            existing_param['type'] = param_type
                    else:
                        # 添加新参数
                        params.append({
                            'name': param_name,
                            'description': description,
                            'type': param_type,
                            'required': True,  # 默认为必需
                            'default': '',
                            'position': position
                        })
                        position += 1
        
        return params
    
    @staticmethod
    def _extract_shell_params(script_content):
        """提取Shell脚本中的参数"""
        params = []
        position = 0
        
        # 查找getopts参数
        getopts_pattern = r'getopts\s+[\'"]([a-zA-Z:]+)[\'"]'
        getopts_match = re.search(getopts_pattern, script_content)
        if getopts_match:
            opts = getopts_match.group(1)
            for i, opt in enumerate(opts):
                if opt == ':':
                    continue
                
                # 检查是否有参数（后面跟着:）
                has_arg = i + 1 < len(opts) and opts[i + 1] == ':'
                
                # 查找该参数的描述
                desc_pattern = rf'# -{opt}: (.*?)(?:\n|$)'
                desc_match = re.search(desc_pattern, script_content)
                description = desc_match.group(1) if desc_match else ''
                
                params.append({
                    'name': opt,
                    'description': description,
                    'type': 'string' if has_arg else 'boolean',
                    'required': False,  # getopts参数通常是可选的
                    'default': '',
                    'position': position
                })
                position += 1
        
        # 查找help函数中的参数说明
        help_pattern = r'(?:usage|help)\(\)\s*{\s*(.*?)\s*}'
        help_match = re.search(help_pattern, script_content, re.DOTALL)
        if help_match:
            help_text = help_match.group(1)
            param_lines = re.finditer(r'\s*-(\w)\s+(?:--(\w+))?\s+(.*?)(?=\n|$)', help_text)
            
            for param_line in param_lines:
                short_opt = param_line.group(1)
                long_opt = param_line.group(2) or ''
                description = param_line.group(3).strip()
                
                param_name = long_opt if long_opt else short_opt
                
                # 检查参数是否已存在
                existing_param = next((p for p in params if p['name'] == short_opt), None)
                if existing_param:
                    # 更新现有参数
                    existing_param['name'] = param_name  # 优先使用长选项名
                    if not existing_param['description']:
                        existing_param['description'] = description
                else:
                    # 添加新参数
                    params.append({
                        'name': param_name,
                        'description': description,
                        'type': 'string',  # 默认为字符串类型
                        'required': False,  # 默认为可选
                        'default': '',
                        'position': position
                    })
                    position += 1
        
        # 查找位置参数
        for i in range(1, 10):  # 检查$1到$9
            param_pattern = rf'\$({i})'
            if re.search(param_pattern, script_content):
                # 查找该参数的描述
                desc_pattern = rf'# Param {i}: (.*?)(?:\n|$)'
                desc_match = re.search(desc_pattern, script_content)
                description = desc_match.group(1) if desc_match else f'位置参数 {i}'
                
                params.append({
                    'name': f'arg{i}',
                    'description': description,
                    'type': 'string',
                    'required': i == 1,  # 第一个参数通常是必需的
                    'default': '',
                    'position': 100 + i  # 位置参数放在最后
                })
        
        return params
    
    @staticmethod
    def _extract_js_params(script_content):
        """提取JavaScript脚本中的参数"""
        params = []
        position = 0
        
        # 查找commander参数
        if 'commander' in script_content or 'program' in script_content:
            # 查找.option调用
            pattern = r'\.option\([\'"](-{1,2}[^\'",]+)(?:,\s*[\'"]([^\'",]+)[\'"])?(?:,\s*[\'"]([^\'",]+)[\'"])?\s*(?:,\s*([^)]+))?\)'
            matches = re.finditer(pattern, script_content)
            
            for match in matches:
                param_name = match.group(1).lstrip('-')
                if '--' in match.group(1):  # 长选项
                    param_name = param_name.split(' ')[0]  # 去除可能的参数描述
                
                description = match.group(3) or match.group(2) or ''
                if description and ('<' in description or '[' in description):
                    description = ''  # 这可能是参数格式而不是描述
                
                default_value = ''
                required = False
                
                # 检查是否有默认值
                if match.group(4):
                    default_match = re.search(r'default:\s*[\'"]?([^\'",)]+)[\'"]?', match.group(4))
                    if default_match:
                        default_value = default_match.group(1)
                    
                    # 检查是否必需
                    required = 'required' in match.group(4)
                
                params.append({
                    'name': param_name,
                    'description': description,
                    'type': 'string',  # 默认为字符串类型
                    'required': required,
                    'default': default_value,
                    'position': position
                })
                position += 1
        
        # 查找JSDoc参数
        jsdoc_pattern = r'/\*\*(.*?)\*/'
        jsdoc_matches = re.finditer(jsdoc_pattern, script_content, re.DOTALL)
        
        for jsdoc_match in jsdoc_matches:
            jsdoc = jsdoc_match.group(1)
            param_matches = re.finditer(r'@param\s+(?:{([^}]+)})?\s+(?:\[([^\]]+)\]|(\S+))\s+(.*?)(?=\n\s*@|\n\s*\*/|$)', jsdoc, re.DOTALL)
            
            for param_match in param_matches:
                param_type = param_match.group(1) or 'string'
                param_name = param_match.group(3) or param_match.group(2) or ''
                if param_name.startswith('[') and param_name.endswith(']'):
                    param_name = param_name[1:-1]
                    required = False
                else:
                    required = True
                
                # 检查是否有默认值
                default_value = ''
                if '=' in param_name:
                    param_name, default_value = param_name.split('=', 1)
                
                description = param_match.group(4).strip()
                
                # 检查参数是否已存在
                existing_param = next((p for p in params if p['name'] == param_name), None)
                if existing_param:
                    # 更新现有参数
                    if not existing_param['description']:
                        existing_param['description'] = description
                    if existing_param['type'] == 'string' and param_type:
                        existing_param['type'] = param_type
                    if not existing_param['default'] and default_value:
                        existing_param['default'] = default_value
                    existing_param['required'] = existing_param['required'] or required
                else:
                    # 添加新参数
                    params.append({
                        'name': param_name,
                        'description': description,
                        'type': param_type,
                        'required': required,
                        'default': default_value,
                        'position': position
                    })
                    position += 1
        
        return params
    
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
