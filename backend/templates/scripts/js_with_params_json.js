#!/usr/bin/env node
// 脚本模板 - 带参数，JSON输出
// 此脚本演示如何处理标准化参数结构并以JSON格式返回结果

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

  // 提取标准化参数结构
  const userParams = paramsData.user_params || {};
  const systemParams = paramsData.system_params || {};
  const fileParams = paramsData.file_params || {};
  
  // 从用户参数中提取具体值（添加默认值保护）
  const name = userParams.name || 'World';
  const value = userParams.value !== undefined ? userParams.value : 42;
  
  // 提取系统参数
  const prevOutput = systemParams.__prev_output;
  const executionTime = systemParams.__execution_time;
  
  // 处理上一个脚本的输出（如果有）
  let prevResult = null;
  if (prevOutput) {
    // 从前一个脚本的输出中提取信息
    if (typeof prevOutput === 'object' && prevOutput !== null) {
      prevResult = prevOutput.message || '无前序消息';
    } else {
      prevResult = String(prevOutput);
    }
  }
  
  // 处理业务逻辑
  const result = {
    message: `Hello, ${name}!`,
    value: value * 2,
    processed_at: new Date().toISOString(),
    status: "success"
  };
  
  // 添加前一个脚本的处理结果（如果有）
  if (prevResult) {
    result.prev_output_processed = true;
    result.prev_result = prevResult;
  }
  
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
