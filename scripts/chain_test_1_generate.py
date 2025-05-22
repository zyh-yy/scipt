#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本链测试 - 第1步：数据生成
用于测试脚本链执行能力，生成随机测试数据供后续处理
"""
import sys
import json
import random
import datetime
import uuid

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
    
    # 获取数据生成参数
    data_count = params.get("data_count", 20)  # 默认生成20条数据
    include_errors = params.get("include_errors", False)  # 是否包含错误数据
    error_rate = params.get("error_rate", 10)  # 错误率（百分比）
    data_type = params.get("data_type", "sensor")  # 数据类型（sensor, transaction, log）
    
    # 输出开始执行信息
    start_info = {
        "script_type": "脚本链测试 - 数据生成",
        "stage": "第1步",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "params_received": params
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 生成数据
    try:
        if data_type == "sensor":
            generated_data = generate_sensor_data(data_count, include_errors, error_rate)
        elif data_type == "transaction":
            generated_data = generate_transaction_data(data_count, include_errors, error_rate)
        elif data_type == "log":
            generated_data = generate_log_data(data_count, include_errors, error_rate)
        else:
            print(json.dumps({"error": f"不支持的数据类型: {data_type}"}))
            return 1
        
        # 构建结果
        result = {
            "script_type": "脚本链测试 - 数据生成",
            "stage": "第1步",
            "status": "成功",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_type": data_type,
            "data_count": len(generated_data),
            "include_errors": include_errors,
            "error_rate": error_rate if include_errors else 0,
            "data": generated_data,
            "chain_id": str(uuid.uuid4()),  # 生成唯一ID用于追踪链执行
            "chain_timestamp": datetime.datetime.now().isoformat()
        }
        
        # 输出结果
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        import traceback
        error_info = {
            "script_type": "脚本链测试 - 数据生成",
            "stage": "第1步",
            "status": "失败",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_info, ensure_ascii=False, indent=2))
        return 1

def generate_sensor_data(count, include_errors, error_rate):
    """生成传感器数据"""
    sensor_types = ["temperature", "humidity", "pressure", "light", "motion"]
    locations = ["room1", "room2", "room3", "outside", "basement"]
    
    data = []
    
    for i in range(count):
        # 确定是否为错误数据
        is_error = include_errors and random.randint(1, 100) <= error_rate
        
        # 生成基本数据
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=i)
        sensor_type = random.choice(sensor_types)
        location = random.choice(locations)
        
        # 根据传感器类型生成合理值
        if sensor_type == "temperature":
            value = random.uniform(15.0, 30.0)
            unit = "°C"
        elif sensor_type == "humidity":
            value = random.uniform(30.0, 80.0)
            unit = "%"
        elif sensor_type == "pressure":
            value = random.uniform(980.0, 1030.0)
            unit = "hPa"
        elif sensor_type == "light":
            value = random.uniform(0.0, 1000.0)
            unit = "lux"
        elif sensor_type == "motion":
            value = random.choice([0, 1])
            unit = "boolean"
        
        # 如果是错误数据，修改值使其异常
        if is_error:
            if sensor_type == "temperature":
                value = random.choice([random.uniform(-50.0, -10.0), random.uniform(50.0, 100.0)])
            elif sensor_type == "humidity":
                value = random.choice([random.uniform(-20.0, -1.0), random.uniform(101.0, 150.0)])
            elif sensor_type == "pressure":
                value = random.choice([random.uniform(0.0, 800.0), random.uniform(1200.0, 2000.0)])
            elif sensor_type == "light":
                value = random.uniform(2000.0, 10000.0)
            # motion传感器不生成错误数据，因为它是布尔值
        
        # 构建数据项
        data_item = {
            "id": i + 1,
            "timestamp": timestamp.isoformat(),
            "sensor_type": sensor_type,
            "location": location,
            "value": value,
            "unit": unit,
            "battery": random.uniform(0.0, 100.0),
            "is_error": is_error
        }
        
        data.append(data_item)
    
    return data

def generate_transaction_data(count, include_errors, error_rate):
    """生成交易数据"""
    transaction_types = ["purchase", "refund", "transfer", "payment", "withdrawal"]
    payment_methods = ["credit_card", "debit_card", "cash", "bank_transfer", "mobile_payment"]
    currencies = ["CNY", "USD", "EUR", "JPY", "GBP"]
    
    data = []
    
    for i in range(count):
        # 确定是否为错误数据
        is_error = include_errors and random.randint(1, 100) <= error_rate
        
        # 生成基本数据
        timestamp = datetime.datetime.now() - datetime.timedelta(hours=i)
        transaction_type = random.choice(transaction_types)
        payment_method = random.choice(payment_methods)
        currency = random.choice(currencies)
        
        # 生成交易金额
        amount = round(random.uniform(10.0, 1000.0), 2)
        
        # 生成交易ID
        transaction_id = f"TRX-{random.randint(100000, 999999)}"
        
        # 如果是错误数据，修改值使其异常
        if is_error:
            # 随机选择错误类型
            error_type = random.choice(["negative_amount", "invalid_id", "missing_method"])
            
            if error_type == "negative_amount":
                amount = round(random.uniform(-1000.0, -0.01), 2)
            elif error_type == "invalid_id":
                transaction_id = None
            elif error_type == "missing_method":
                payment_method = None
        
        # 构建数据项
        data_item = {
            "id": i + 1,
            "transaction_id": transaction_id,
            "timestamp": timestamp.isoformat(),
            "transaction_type": transaction_type,
            "payment_method": payment_method,
            "amount": amount,
            "currency": currency,
            "status": "completed" if not is_error else "error",
            "is_error": is_error
        }
        
        data.append(data_item)
    
    return data

def generate_log_data(count, include_errors, error_rate):
    """生成日志数据"""
    log_levels = ["INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"]
    services = ["web-server", "database", "auth-service", "cache", "api-gateway"]
    
    data = []
    
    for i in range(count):
        # 确定是否为错误数据
        is_error = include_errors and random.randint(1, 100) <= error_rate
        
        # 生成基本数据
        timestamp = datetime.datetime.now() - datetime.timedelta(seconds=i*30)
        
        # 如果是错误数据，让它是ERROR或CRITICAL日志级别
        if is_error:
            log_level = random.choice(["ERROR", "CRITICAL"])
        else:
            # 非错误数据可以是任何日志级别
            log_level = random.choice(log_levels)
        
        service = random.choice(services)
        
        # 根据日志级别和服务生成合适的消息
        if log_level == "INFO":
            messages = [
                f"{service} started successfully",
                f"User login successful",
                f"Database connection established",
                f"Cache refresh completed",
                f"API request processed"
            ]
        elif log_level == "WARNING":
            messages = [
                f"High CPU usage in {service}",
                f"Slow database query detected",
                f"Cache miss rate increased",
                f"API rate limit approaching",
                f"Low disk space warning"
            ]
        elif log_level == "ERROR":
            messages = [
                f"Failed to connect to {service}",
                f"Database query error",
                f"Authentication failed",
                f"API request timeout",
                f"Service unavailable"
            ]
        elif log_level == "DEBUG":
            messages = [
                f"Processing request parameters",
                f"SQL query execution time: {random.uniform(0.1, 2.0):.2f}s",
                f"Cache hit rate: {random.uniform(50, 99):.1f}%",
                f"Memory usage: {random.randint(100, 500)}MB",
                f"Thread pool size: {random.randint(5, 50)}"
            ]
        elif log_level == "CRITICAL":
            messages = [
                f"{service} crashed unexpectedly",
                f"Database connection lost",
                f"Out of memory error",
                f"System overload detected",
                f"Security breach detected"
            ]
        
        message = random.choice(messages)
        
        # 构建数据项
        data_item = {
            "id": i + 1,
            "timestamp": timestamp.isoformat(),
            "log_level": log_level,
            "service": service,
            "message": message,
            "is_error": is_error or log_level in ["ERROR", "CRITICAL"]
        }
        
        data.append(data_item)
    
    return data

if __name__ == "__main__":
    sys.exit(main())
