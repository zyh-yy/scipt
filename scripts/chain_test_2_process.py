#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本链测试 - 第2步：数据处理
用于测试脚本链执行能力，处理上一步生成的数据
"""
import sys
import json
import datetime
import statistics
from collections import Counter

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
    
    # 获取上一步传递的数据
    prev_output = params.get("__prev_output")
    
    if not prev_output:
        print(json.dumps({"error": "缺少上一步的输出数据"}))
        return 1
    
    # 如果prev_output是字符串，尝试解析成JSON
    if isinstance(prev_output, str):
        try:
            prev_output = json.loads(prev_output)
        except Exception as e:
            print(json.dumps({"error": f"无法解析上一步的输出数据: {str(e)}"}))
            return 1
    
    # 输出开始执行信息
    start_info = {
        "script_type": "脚本链测试 - 数据处理",
        "stage": "第2步",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prev_stage": prev_output.get("stage", "未知"),
        "data_type": prev_output.get("data_type", "未知"),
        "data_count": prev_output.get("data_count", 0),
        "chain_id": prev_output.get("chain_id", "未知")
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 获取数据
    data = prev_output.get("data", [])
    data_type = prev_output.get("data_type", "unknown")
    
    if not data:
        print(json.dumps({"error": "上一步未生成有效数据"}))
        return 1
    
    # 处理数据
    try:
        if data_type == "sensor":
            processed_result = process_sensor_data(data)
        elif data_type == "transaction":
            processed_result = process_transaction_data(data)
        elif data_type == "log":
            processed_result = process_log_data(data)
        else:
            print(json.dumps({"error": f"不支持的数据类型: {data_type}"}))
            return 1
        
        # 添加共享信息
        processed_result["script_type"] = "脚本链测试 - 数据处理"
        processed_result["stage"] = "第2步"
        processed_result["status"] = "成功"
        processed_result["execution_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        processed_result["data_type"] = data_type
        processed_result["original_data_count"] = len(data)
        processed_result["chain_id"] = prev_output.get("chain_id", "未知")
        processed_result["chain_timestamp"] = prev_output.get("chain_timestamp", datetime.datetime.now().isoformat())
        processed_result["original_data"] = data  # 保留原始数据，以便下一步使用
        
        # 输出结果
        print(json.dumps(processed_result, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        import traceback
        error_info = {
            "script_type": "脚本链测试 - 数据处理",
            "stage": "第2步",
            "status": "失败",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
            "traceback": traceback.format_exc(),
            "chain_id": prev_output.get("chain_id", "未知")
        }
        print(json.dumps(error_info, ensure_ascii=False, indent=2))
        return 1

def process_sensor_data(data):
    """处理传感器数据"""
    result = {"success": True, "data_analyses": {}}
    
    # 按传感器类型分组数据
    sensor_types = set(item["sensor_type"] for item in data)
    
    # 处理每种类型的传感器数据
    for sensor_type in sensor_types:
        # 提取该类型的传感器数据
        sensor_data = [item for item in data if item["sensor_type"] == sensor_type]
        
        # 分离正常数据和错误数据
        normal_data = [item for item in sensor_data if not item["is_error"]]
        error_data = [item for item in sensor_data if item["is_error"]]
        
        # 计算基本统计信息（只使用正常数据）
        values = [item["value"] for item in normal_data]
        
        if values:
            stats = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": statistics.median(values) if len(values) > 0 else None,
                "stddev": statistics.stdev(values) if len(values) > 1 else 0
            }
        else:
            stats = {
                "count": 0,
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "stddev": None
            }
        
        # 按位置分析
        locations = set(item["location"] for item in sensor_data)
        location_stats = {}
        
        for location in locations:
            location_data = [item for item in sensor_data if item["location"] == location]
            location_normal = [item for item in location_data if not item["is_error"]]
            location_values = [item["value"] for item in location_normal]
            
            if location_values:
                location_stats[location] = {
                    "count": len(location_values),
                    "min": min(location_values),
                    "max": max(location_values),
                    "mean": sum(location_values) / len(location_values),
                    "error_count": len(location_data) - len(location_normal)
                }
            else:
                location_stats[location] = {
                    "count": 0,
                    "min": None,
                    "max": None,
                    "mean": None,
                    "error_count": len(location_data)
                }
        
        # 汇总该类型传感器的分析结果
        result["data_analyses"][sensor_type] = {
            "total_count": len(sensor_data),
            "normal_count": len(normal_data),
            "error_count": len(error_data),
            "error_rate": round(len(error_data) / len(sensor_data) * 100, 2) if sensor_data else 0,
            "statistics": stats,
            "by_location": location_stats,
            "unit": sensor_data[0]["unit"] if sensor_data else "unknown"
        }
    
    # 计算异常检测
    # 对于每种类型的传感器和位置组合，标记偏离均值超过2个标准差的数据点
    anomalies = []
    
    for item in data:
        sensor_type = item["sensor_type"]
        location = item["location"]
        
        # 获取相同类型和位置的数据点
        similar_data = [i for i in data if i["sensor_type"] == sensor_type and i["location"] == location and not i["is_error"]]
        
        if len(similar_data) >= 3:  # 需要足够的样本
            values = [i["value"] for i in similar_data]
            mean = sum(values) / len(values)
            stddev = statistics.stdev(values)
            
            # 检查当前值是否是异常值（超过2个标准差）
            if not item["is_error"] and abs(item["value"] - mean) > 2 * stddev:
                anomalies.append({
                    "id": item["id"],
                    "sensor_type": sensor_type,
                    "location": location,
                    "value": item["value"],
                    "mean": mean,
                    "stddev": stddev,
                    "deviation": abs(item["value"] - mean) / stddev,
                    "timestamp": item["timestamp"]
                })
    
    result["anomalies"] = anomalies
    result["anomaly_count"] = len(anomalies)
    
    # 生成处理后的数据集
    processed_data = []
    
    for item in data:
        # 复制原始数据
        processed_item = item.copy()
        
        # 添加额外信息
        sensor_type = item["sensor_type"]
        stats = result["data_analyses"][sensor_type]["statistics"]
        
        if not item["is_error"] and stats["mean"] is not None and stats["stddev"] is not None:
            # 计算z得分（标准分数）
            z_score = (item["value"] - stats["mean"]) / stats["stddev"] if stats["stddev"] > 0 else 0
            
            # 添加处理信息
            processed_item["processed"] = True
            processed_item["z_score"] = z_score
            processed_item["deviation_from_mean"] = item["value"] - stats["mean"]
            processed_item["is_anomaly"] = any(a["id"] == item["id"] for a in anomalies)
            
            # 相对于最大值和最小值的百分比
            if stats["max"] != stats["min"]:
                processed_item["percent_of_range"] = (item["value"] - stats["min"]) / (stats["max"] - stats["min"]) * 100
            else:
                processed_item["percent_of_range"] = 100 if item["value"] == stats["max"] else 0
        else:
            processed_item["processed"] = False
            processed_item["z_score"] = None
            processed_item["deviation_from_mean"] = None
            processed_item["is_anomaly"] = None
            processed_item["percent_of_range"] = None
        
        processed_data.append(processed_item)
    
    result["processed_data"] = processed_data
    
    return result

def process_transaction_data(data):
    """处理交易数据"""
    result = {"success": True, "data_analyses": {}}
    
    # 分离正常交易和错误交易
    normal_transactions = [item for item in data if not item["is_error"]]
    error_transactions = [item for item in data if item["is_error"]]
    
    # 按交易类型统计
    transaction_types = set(item["transaction_type"] for item in data)
    type_stats = {}
    
    for t_type in transaction_types:
        type_data = [item for item in data if item["transaction_type"] == t_type]
        type_normal = [item for item in type_data if not item["is_error"]]
        
        # 计算该类型的金额统计
        amounts = [item["amount"] for item in type_normal]
        
        if amounts:
            type_stats[t_type] = {
                "count": len(type_data),
                "normal_count": len(type_normal),
                "error_count": len(type_data) - len(type_normal),
                "total_amount": sum(amounts),
                "min_amount": min(amounts),
                "max_amount": max(amounts),
                "avg_amount": sum(amounts) / len(amounts)
            }
        else:
            type_stats[t_type] = {
                "count": len(type_data),
                "normal_count": 0,
                "error_count": len(type_data),
                "total_amount": 0,
                "min_amount": None,
                "max_amount": None,
                "avg_amount": None
            }
    
    # 按支付方式统计
    payment_methods = {}
    for item in normal_transactions:
        method = item["payment_method"]
        if method:  # 忽略支付方式为None的情况
            if method not in payment_methods:
                payment_methods[method] = {
                    "count": 0,
                    "total_amount": 0
                }
            payment_methods[method]["count"] += 1
            payment_methods[method]["total_amount"] += item["amount"]
    
    # 按货币统计
    currencies = {}
    for item in normal_transactions:
        currency = item["currency"]
        if currency not in currencies:
            currencies[currency] = {
                "count": 0,
                "total_amount": 0
            }
        currencies[currency]["count"] += 1
        currencies[currency]["total_amount"] += item["amount"]
    
    # 计算总金额和平均值
    if normal_transactions:
        total_amount = sum(item["amount"] for item in normal_transactions)
        avg_amount = total_amount / len(normal_transactions)
    else:
        total_amount = 0
        avg_amount = 0
    
    # 汇总统计结果
    result["data_analyses"] = {
        "total_count": len(data),
        "normal_count": len(normal_transactions),
        "error_count": len(error_transactions),
        "error_rate": round(len(error_transactions) / len(data) * 100, 2) if data else 0,
        "total_amount": total_amount,
        "avg_amount": avg_amount,
        "by_type": type_stats,
        "by_payment_method": payment_methods,
        "by_currency": currencies
    }
    
    # 生成处理后的数据集
    processed_data = []
    
    for item in data:
        # 复制原始数据
        processed_item = item.copy()
        
        # 添加额外处理信息
        if not item["is_error"]:
            t_type = item["transaction_type"]
            type_avg = type_stats[t_type]["avg_amount"]
            
            processed_item["processed"] = True
            processed_item["deviation_from_type_avg"] = item["amount"] - type_avg
            
            # 相对于平均交易金额的百分比
            if avg_amount > 0:
                processed_item["percent_of_avg"] = (item["amount"] / avg_amount) * 100
            else:
                processed_item["percent_of_avg"] = 0
                
            # 相对于该类型最大交易的百分比
            type_max = type_stats[t_type]["max_amount"]
            if type_max > 0:
                processed_item["percent_of_type_max"] = (item["amount"] / type_max) * 100
            else:
                processed_item["percent_of_type_max"] = 0
        else:
            processed_item["processed"] = False
            processed_item["deviation_from_type_avg"] = None
            processed_item["percent_of_avg"] = None
            processed_item["percent_of_type_max"] = None
        
        processed_data.append(processed_item)
    
    result["processed_data"] = processed_data
    
    return result

def process_log_data(data):
    """处理日志数据"""
    result = {"success": True, "data_analyses": {}}
    
    # 按日志级别统计
    log_levels = {}
    for item in data:
        level = item["log_level"]
        if level not in log_levels:
            log_levels[level] = 0
        log_levels[level] += 1
    
    # 按服务统计
    services = {}
    for item in data:
        service = item["service"]
        if service not in services:
            services[service] = {
                "total": 0,
                "by_level": {}
            }
        services[service]["total"] += 1
        
        # 按服务和级别统计
        level = item["log_level"]
        if level not in services[service]["by_level"]:
            services[service]["by_level"][level] = 0
        services[service]["by_level"][level] += 1
    
    # 识别常见错误模式
    error_logs = [item for item in data if item["is_error"]]
    error_messages = [item["message"] for item in error_logs]
    error_patterns = Counter(error_messages).most_common(5)
    
    # 按时间段统计
    time_series = {}
    for item in data:
        # 提取小时
        timestamp = item["timestamp"]
        hour = timestamp.split("T")[1].split(":")[0]
        
        if hour not in time_series:
            time_series[hour] = {
                "total": 0,
                "error": 0,
                "warning": 0,
                "info": 0,
                "other": 0
            }
        
        time_series[hour]["total"] += 1
        
        if item["log_level"] == "ERROR" or item["log_level"] == "CRITICAL":
            time_series[hour]["error"] += 1
        elif item["log_level"] == "WARNING":
            time_series[hour]["warning"] += 1
        elif item["log_level"] == "INFO":
            time_series[hour]["info"] += 1
        else:
            time_series[hour]["other"] += 1
    
    # 汇总统计结果
    result["data_analyses"] = {
        "total_logs": len(data),
        "error_logs": len([item for item in data if item["is_error"]]),
        "error_rate": round(len([item for item in data if item["is_error"]]) / len(data) * 100, 2) if data else 0,
        "by_level": log_levels,
        "by_service": services,
        "error_patterns": [{"message": msg, "count": count} for msg, count in error_patterns],
        "time_series": time_series
    }
    
    # 对日志进行分类处理
    processed_data = []
    
    for item in data:
        # 复制原始数据
        processed_item = item.copy()
        
        # 添加额外信息
        processed_item["processed"] = True
        
        # 简单的关键词分类
        if "error" in item["message"].lower() or "fail" in item["message"].lower() or "exception" in item["message"].lower():
            processed_item["category"] = "error_related"
        elif "warn" in item["message"].lower() or "slow" in item["message"].lower() or "limit" in item["message"].lower():
            processed_item["category"] = "warning_related"
        elif "start" in item["message"].lower() or "success" in item["message"].lower() or "complete" in item["message"].lower():
            processed_item["category"] = "success_related"
        else:
            processed_item["category"] = "other"
        
        # 添加优先级评分
        if item["log_level"] == "CRITICAL":
            processed_item["priority_score"] = 5
        elif item["log_level"] == "ERROR":
            processed_item["priority_score"] = 4
        elif item["log_level"] == "WARNING":
            processed_item["priority_score"] = 3
        elif item["log_level"] == "INFO":
            processed_item["priority_score"] = 2
        else:
            processed_item["priority_score"] = 1
        
        processed_data.append(processed_item)
    
    result["processed_data"] = processed_data
    
    return result

if __name__ == "__main__":
    sys.exit(main())
