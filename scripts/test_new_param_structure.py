#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新的标准化参数传递功能
此脚本会执行一系列测试，验证新的参数传递机制是否正常工作
"""
import os
import sys
import json
import time
import tempfile
from pathlib import Path

# 获取项目根目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)

# 导入项目配置和脚本执行器
from config import logger
from backend.utils.script_runner import ScriptRunner

def create_test_script(script_type):
    """创建测试脚本文件
    
    Args:
        script_type: 脚本类型 (py, sh, js)
        
    Returns:
        str: 脚本文件路径
    """
    temp_dir = tempfile.gettempdir()
    
    if script_type == 'py':
        # 使用Python模板创建脚本
        script_content = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本参数测试 - Python版
"""
import sys
import json
import os
from datetime import datetime

def main():
    """主函数"""
    # 检查参数文件是否存在
    if len(sys.argv) < 2:
        print(json.dumps({"error": "参数文件不存在"}))
        return 1
    
    params_file = sys.argv[1]
    if not os.path.exists(params_file):
        print(json.dumps({"error": f"参数文件不存在: {params_file}"}))
        return 1
    
    # 读取参数
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params_data = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"读取参数失败: {str(e)}"}))
        return 1
    
    # 输出完整的参数结构（用于测试）
    result = {
        "params_received": params_data,
        "execution_time": datetime.now().isoformat(),
        "script_type": "Python"
    }
    
    # 以JSON格式返回结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        script_path = os.path.join(temp_dir, f"test_params_{time.time()}.py")
        
    elif script_type == 'sh':
        # 使用Shell模板创建脚本
        script_content = '''#!/bin/bash
# 脚本参数测试 - Shell版

# 检查参数文件
if [ $# -lt 1 ]; then
  echo "{\"error\": \"参数文件不存在\"}"
  exit 1
fi

PARAMS_FILE=$1
if [ ! -f "$PARAMS_FILE" ]; then
  echo "{\"error\": \"参数文件不存在: $PARAMS_FILE\"}"
  exit 1
fi

# 读取参数文件内容
PARAMS_CONTENT=$(cat "$PARAMS_FILE")

# 构建输出结果
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
RESULT="{
  \"params_received\": $PARAMS_CONTENT,
  \"execution_time\": \"$TIMESTAMP\",
  \"script_type\": \"Shell\"
}"

echo "$RESULT"
exit 0
'''
        script_path = os.path.join(temp_dir, f"test_params_{time.time()}.sh")
        
    elif script_type == 'js':
        # 使用JavaScript模板创建脚本
        script_content = '''#!/usr/bin/env node
// 脚本参数测试 - JavaScript版

const fs = require('fs');

// 主函数
async function main() {
  // 检查参数文件
  if (process.argv.length < 3) {
    console.error(JSON.stringify({"error": "参数文件不存在"}));
    return 1;
  }

  const paramsFile = process.argv[2];
  
  // 检查文件是否存在
  if (!fs.existsSync(paramsFile)) {
    console.error(JSON.stringify({"error": `参数文件不存在: ${paramsFile}`}));
    return 1;
  }

  // 读取参数
  let paramsData;
  try {
    const fileContent = fs.readFileSync(paramsFile, 'utf8');
    paramsData = JSON.parse(fileContent);
  } catch (e) {
    console.error(JSON.stringify({"error": `读取参数失败: ${e.message}`}));
    return 1;
  }

  // 输出完整的参数结构（用于测试）
  const result = {
    params_received: paramsData,
    execution_time: new Date().toISOString(),
    script_type: "JavaScript"
  };
  
  // 输出JSON结果
  console.log(JSON.stringify(result, null, 2));
  return 0;
}

// 执行主函数
main().then(exitCode => {
  process.exit(exitCode);
}).catch(error => {
  console.error(JSON.stringify({error: error.message}));
  process.exit(1);
});
'''
        script_path = os.path.join(temp_dir, f"test_params_{time.time()}.js")
    
    else:
        raise ValueError(f"不支持的脚本类型: {script_type}")
    
    # 写入脚本文件
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 如果是Shell脚本，确保有执行权限
    if script_type == 'sh' and os.name != 'nt':
        os.chmod(script_path, 0o755)
    
    return script_path

def run_test_script(script_path, params):
    """运行测试脚本
    
    Args:
        script_path: 脚本路径
        params: 脚本参数
        
    Returns:
        tuple: (success, output, error)
    """
    print(f"执行脚本: {script_path}")
    print(f"传递参数: {json.dumps(params, ensure_ascii=False)}")
    
    # 使用ScriptRunner执行脚本
    success, output, error = ScriptRunner.run_script(script_path, params)
    
    print(f"执行结果: {'成功' if success else '失败'}")
    if success:
        print(f"输出: {json.dumps(output, ensure_ascii=False, indent=2)}")
    else:
        print(f"错误: {error}")
    
    print("-" * 50)
    return success, output, error

def test_chain_execution(script_paths, params):
    """测试脚本链执行
    
    Args:
        script_paths: 脚本路径列表
        params: 初始参数
        
    Returns:
        tuple: (success, outputs, error)
    """
    print("测试脚本链执行")
    print(f"脚本数量: {len(script_paths)}")
    print(f"初始参数: {json.dumps(params, ensure_ascii=False)}")
    
    # 创建链节点列表
    chain_nodes = []
    for i, path in enumerate(script_paths):
        chain_nodes.append({
            'script_id': i + 1,
            'file_path': path
        })
    
    # 使用ScriptRunner执行脚本链
    success, outputs, error = ScriptRunner.run_script_chain(chain_nodes, params)
    
    print(f"执行结果: {'成功' if success else '失败'}")
    if success:
        print("链执行输出:")
        for script_id, result in outputs.items():
            print(f"脚本 {script_id}:")
            print(f"  成功: {result['success']}")
            print(f"  输出: {json.dumps(result['output'], ensure_ascii=False, indent=2)[:200]}...")
    else:
        print(f"错误: {error}")
    
    print("=" * 50)
    return success, outputs, error

def main():
    """主函数"""
    print("开始测试新的参数传递功能")
    print("=" * 50)
    
    # 创建测试脚本
    python_script = create_test_script('py')
    shell_script = create_test_script('sh')
    js_script = create_test_script('js')
    
    # 准备测试参数
    test_params = {
        'name': '参数测试',
        'value': 100,
        'options': ['option1', 'option2', 'option3'],
        'config': {
            'enabled': True,
            'timeout': 30
        },
        'input_file': 'test_input.txt',
        'output_file': 'test_output.txt'
    }
    
    # 测试单独执行每种类型的脚本
    run_test_script(python_script, test_params)
    run_test_script(shell_script, test_params)
    run_test_script(js_script, test_params)
    
    # 测试脚本链执行
    test_chain_execution([python_script, shell_script, js_script], test_params)
    
    # 清理测试脚本
    for script in [python_script, shell_script, js_script]:
        try:
            os.unlink(script)
        except:
            pass
    
    print("测试完成")
    return 0

if __name__ == "__main__":
    sys.exit(main())
