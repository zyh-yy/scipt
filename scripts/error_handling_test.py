#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
错误处理测试脚本
用于测试系统对脚本执行错误的处理能力
"""
import sys
import json
import os
import random
import datetime
import traceback

def main():
    # 检查参数文件
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数文件"}))
        return 1
    
    params_file = sys.argv[1]
    
    # 读取参数
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"参数读取失败: {str(e)}"}))
        return 1
    
    # 获取错误类型和其他参数
    error_type = params.get("error_type", "none")
    fail_percent = params.get("fail_percent", 50)  # 默认50%的失败率（随机失败时使用）
    error_message = params.get("error_message", "自定义错误信息")
    exit_code = params.get("exit_code", 1)
    
    # 输出开始执行信息
    start_info = {
        "script_type": "错误处理测试",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error_type": error_type,
        "params_received": params
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 根据错误类型执行不同的测试
    try:
        if error_type == "none":
            print(json.dumps({
                "script_type": "错误处理测试",
                "status": "成功",
                "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "脚本执行成功，没有错误",
                "success": True
            }, ensure_ascii=False, indent=2))
            return 0
            
        elif error_type == "exception":
            # 抛出未捕获的异常
            raise Exception(error_message)
            
        elif error_type == "syntax_error":
            # 尝试执行语法错误的代码
            # 以下代码包含语法错误，会在运行时引发SyntaxError
            exec("if True print('这是一个语法错误')")
            
        elif error_type == "name_error":
            # 引用一个不存在的变量，产生NameError
            undefined_variable = not_defined_variable + 1
            
        elif error_type == "zero_division":
            # 除以零错误
            result = 1 / 0
            
        elif error_type == "index_error":
            # 索引错误
            my_list = [1, 2, 3]
            item = my_list[10]
            
        elif error_type == "key_error":
            # 字典键错误
            my_dict = {"a": 1, "b": 2}
            value = my_dict["not_exist_key"]
            
        elif error_type == "file_not_found":
            # 文件不存在错误
            with open("/path/to/non_existent_file.txt", "r") as f:
                content = f.read()
            
        elif error_type == "permission_error":
            # 权限错误
            try:
                # 尝试写入到一个通常需要管理员权限的目录
                with open("/etc/test_permission.txt", "w") as f:
                    f.write("测试内容")
            except PermissionError:
                # 捕获权限错误，但仍然抛出一个错误
                raise PermissionError("没有写入权限：/etc/test_permission.txt")
            
        elif error_type == "import_error":
            # 导入错误
            import non_existent_module
            
        elif error_type == "memory_error":
            # 内存错误 - 尝试分配过多内存
            try:
                # 尝试分配大量内存
                big_list = [0] * (10**9)  # 尝试分配一个大数组
            except MemoryError:
                # 捕获内存错误，但仍然抛出一个错误
                raise MemoryError("内存分配失败")
            
        elif error_type == "timeout":
            # 模拟超时 - 在Docker环境中，实际超时会由执行器处理
            # 这里只是模拟一个会导致实际超时的无限循环
            print(json.dumps({
                "warning": "这将开始一个无限循环，应该由执行器超时终止",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, ensure_ascii=False))
            import time
            while True:
                time.sleep(1)
                
        elif error_type == "random":
            # 随机决定是否成功
            if random.randint(1, 100) <= fail_percent:
                raise Exception(f"随机失败 (失败率: {fail_percent}%)")
            else:
                print(json.dumps({
                    "script_type": "错误处理测试",
                    "status": "成功",
                    "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": f"随机成功 (失败率: {fail_percent}%)",
                    "success": True
                }, ensure_ascii=False, indent=2))
                return 0
                
        elif error_type == "custom_exit":
            # 返回自定义退出码
            print(json.dumps({
                "script_type": "错误处理测试",
                "status": "自定义退出码",
                "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "exit_code": exit_code,
                "message": f"脚本将以自定义退出码 {exit_code} 退出"
            }, ensure_ascii=False, indent=2))
            return exit_code
            
        else:
            # 未知错误类型
            print(json.dumps({
                "script_type": "错误处理测试",
                "status": "失败",
                "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"未知的错误类型: {error_type}",
                "success": False
            }, ensure_ascii=False, indent=2))
            return 1
        
    except Exception as e:
        # 捕获并输出错误信息
        error_info = {
            "script_type": "错误处理测试",
            "status": "失败",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_type": error_type,
            "error_message": str(e),
            "error_class": e.__class__.__name__,
            "traceback": traceback.format_exc(),
            "success": False
        }
        print(json.dumps(error_info, ensure_ascii=False, indent=2))
        return 1
    
    # 如果没有触发任何错误，返回成功（正常情况下不会执行到这里）
    print(json.dumps({
        "script_type": "错误处理测试",
        "status": "成功",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": "脚本执行成功，但期望的错误没有发生",
        "success": True
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
