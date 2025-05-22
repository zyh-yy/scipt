#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本链测试 - 第3步：结果汇总
用于测试脚本链执行能力，汇总前两步的结果并生成报告
"""
import sys
import json
import datetime
import os
import uuid
import math

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
    
    # 获取报告参数
    report_format = params.get("report_format", "json")  # json, summary
    output_file = params.get("output_file", "")  # 如果指定了输出文件，则将报告写入文件
    include_visualization = params.get("include_visualization", False)  # 是否包含可视化代码
    threshold = params.get("threshold", None)  # 用于阈值分析的值
    
    # 输出开始执行信息
    start_info = {
        "script_type": "脚本链测试 - 结果汇总",
        "stage": "第3步",
        "status": "开始",
        "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prev_stage": prev_output.get("stage", "未知"),
        "data_type": prev_output.get("data_type", "未知"),
        "chain_id": prev_output.get("chain_id", "未知")
    }
    print(json.dumps(start_info, ensure_ascii=False, indent=2))
    
    # 获取原始数据和处理后的数据
    data_type = prev_output.get("data_type", "unknown")
    original_data = prev_output.get("original_data", [])
    processed_data = prev_output.get("processed_data", [])
    data_analyses = prev_output.get("data_analyses", {})
    
    if not processed_data:
        print(json.dumps({"error": "上一步未提供有效的处理数据"}))
        return 1
    
    # 生成报告
    try:
        # 根据数据类型生成相应的报告
        if data_type == "sensor":
            report = generate_sensor_report(original_data, processed_data, data_analyses, threshold)
        elif data_type == "transaction":
            report = generate_transaction_report(original_data, processed_data, data_analyses, threshold)
        elif data_type == "log":
            report = generate_log_report(original_data, processed_data, data_analyses, threshold)
        else:
            print(json.dumps({"error": f"不支持的数据类型: {data_type}"}))
            return 1
        
        # 添加可视化代码
        if include_visualization:
            visualization_code = generate_visualization_code(data_type, processed_data, data_analyses)
            report["visualization_code"] = visualization_code
        
        # 添加共享信息
        report["script_type"] = "脚本链测试 - 结果汇总"
        report["stage"] = "第3步"
        report["status"] = "成功"
        report["execution_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report["data_type"] = data_type
        report["chain_id"] = prev_output.get("chain_id", "未知")
        report["chain_timestamp"] = prev_output.get("chain_timestamp", datetime.datetime.now().isoformat())
        report["report_format"] = report_format
        
        # 根据报告格式生成最终输出
        if report_format == "summary":
            final_report = generate_summary_report(report, data_type)
        else:  # json
            final_report = report
        
        # 如果指定了输出文件，则将报告写入文件
        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)
            
            # 在输出中包含文件信息
            final_report["output_file"] = output_file
            final_report["file_size"] = os.path.getsize(output_file)
        
        # 输出结果
        print(json.dumps(final_report, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        import traceback
        error_info = {
            "script_type": "脚本链测试 - 结果汇总",
            "stage": "第3步",
            "status": "失败",
            "execution_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
            "traceback": traceback.format_exc(),
            "chain_id": prev_output.get("chain_id", "未知")
        }
        print(json.dumps(error_info, ensure_ascii=False, indent=2))
        return 1

def generate_sensor_report(original_data, processed_data, analyses, threshold=None):
    """生成传感器数据报告"""
    if threshold is None:
        # 如果未指定阈值，使用不同传感器类型的默认阈值
        sensor_thresholds = {
            "temperature": 28.0,  # 默认28度
            "humidity": 70.0,     # 默认70%
            "pressure": 1010.0,   # 默认1010 hPa
            "light": 800.0,       # 默认800 lux
            "motion": 0.5         # 默认0.5（布尔传感器的阈值）
        }
    else:
        # 使用用户指定的阈值
        sensor_thresholds = {
            "temperature": threshold,
            "humidity": threshold,
            "pressure": threshold,
            "light": threshold,
            "motion": threshold
        }
    
    # 构建报告基本结构
    report = {
        "report_title": "传感器数据分析报告",
        "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "total_sensors": len(set(item["sensor_type"] for item in original_data)),
            "total_locations": len(set(item["location"] for item in original_data)),
            "total_readings": len(original_data),
            "normal_readings": len([item for item in original_data if not item["is_error"]]),
            "error_readings": len([item for item in original_data if item["is_error"]]),
            "error_rate": round(len([item for item in original_data if item["is_error"]]) / len(original_data) * 100, 2) if original_data else 0,
            "time_range": {
                "start": min(item["timestamp"] for item in original_data) if original_data else None,
                "end": max(item["timestamp"] for item in original_data) if original_data else None
            }
        },
        "analyses": analyses
    }
    
    # 添加异常检测结果
    anomalies = [item for item in processed_data if item.get("is_anomaly")]
    
    # 构建阈值分析
    threshold_analysis = {}
    for sensor_type in analyses.keys():
        # 获取该类型的传感器数据
        sensor_data = [item for item in processed_data if item["sensor_type"] == sensor_type and not item["is_error"]]
        threshold = sensor_thresholds.get(sensor_type)
        
        if not sensor_data or threshold is None:
            continue
        
        # 计算超过阈值的数据点
        above_threshold = [item for item in sensor_data if item["value"] > threshold]
        below_threshold = [item for item in sensor_data if item["value"] <= threshold]
        
        threshold_analysis[sensor_type] = {
            "threshold": threshold,
            "above_threshold_count": len(above_threshold),
            "below_threshold_count": len(below_threshold),
            "above_threshold_percent": round(len(above_threshold) / len(sensor_data) * 100, 2) if sensor_data else 0,
            "units": sensor_data[0]["unit"] if sensor_data else "unknown"
        }
    
    # 添加分析结果
    report["threshold_analysis"] = threshold_analysis
    report["anomaly_count"] = len(anomalies)
    report["anomaly_rate"] = round(len(anomalies) / len([item for item in processed_data if not item["is_error"]]) * 100, 2) if processed_data else 0
    
    # 提取关键发现
    key_findings = []
    
    # 1. 检查错误率
    if report["data_summary"]["error_rate"] > 10:
        key_findings.append({
            "type": "error_rate",
            "message": f"较高错误率: {report['data_summary']['error_rate']}%传感器读数存在错误",
            "severity": "high"
        })
    
    # 2. 检查异常值
    if report["anomaly_rate"] > 5:
        key_findings.append({
            "type": "anomalies",
            "message": f"较多异常值: {report['anomaly_rate']}%的有效读数为异常值",
            "severity": "medium"
        })
    
    # 3. 检查阈值分析
    for sensor_type, analysis in threshold_analysis.items():
        if analysis["above_threshold_percent"] > 50:
            key_findings.append({
                "type": "threshold",
                "message": f"{sensor_type}传感器: {analysis['above_threshold_percent']}%的读数超过阈值({analysis['threshold']}{analysis['units']})",
                "severity": "medium"
            })
    
    # 添加关键发现
    report["key_findings"] = key_findings
    
    # 生成建议
    recommendations = []
    
    if report["data_summary"]["error_rate"] > 5:
        recommendations.append("检查传感器状态，部分传感器可能需要维护或更换")
    
    if report["anomaly_rate"] > 5:
        recommendations.append("调查异常读数的可能原因，如环境变化或传感器问题")
    
    for sensor_type, analysis in threshold_analysis.items():
        if analysis["above_threshold_percent"] > 30:
            if sensor_type == "temperature":
                recommendations.append(f"考虑调整温度控制系统，当前{analysis['above_threshold_percent']}%的温度读数超过{analysis['threshold']}{analysis['units']}")
            elif sensor_type == "humidity":
                recommendations.append(f"检查湿度控制系统，当前{analysis['above_threshold_percent']}%的湿度读数超过{analysis['threshold']}{analysis['units']}")
    
    report["recommendations"] = recommendations
    
    return report

def generate_transaction_report(original_data, processed_data, analyses, threshold=None):
    """生成交易数据报告"""
    if threshold is None:
        # 如果未指定阈值，使用默认金额阈值
        amount_threshold = 500.0  # 默认500货币单位
    else:
        # 使用用户指定的阈值
        amount_threshold = float(threshold)
    
    # 构建报告基本结构
    report = {
        "report_title": "交易数据分析报告",
        "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "total_transactions": len(original_data),
            "normal_transactions": len([item for item in original_data if not item["is_error"]]),
            "error_transactions": len([item for item in original_data if item["is_error"]]),
            "error_rate": round(len([item for item in original_data if item["is_error"]]) / len(original_data) * 100, 2) if original_data else 0,
            "transaction_types": list(set(item["transaction_type"] for item in original_data)),
            "time_range": {
                "start": min(item["timestamp"] for item in original_data) if original_data else None,
                "end": max(item["timestamp"] for item in original_data) if original_data else None
            }
        },
        "analyses": analyses
    }
    
    # 构建金额阈值分析
    valid_transactions = [item for item in processed_data if not item["is_error"]]
    large_transactions = [item for item in valid_transactions if item["amount"] > amount_threshold]
    
    threshold_analysis = {
        "threshold": amount_threshold,
        "total_valid_transactions": len(valid_transactions),
        "large_transactions_count": len(large_transactions),
        "large_transactions_percent": round(len(large_transactions) / len(valid_transactions) * 100, 2) if valid_transactions else 0,
        "large_transactions_total": sum(item["amount"] for item in large_transactions),
        "large_transactions_avg": sum(item["amount"] for item in large_transactions) / len(large_transactions) if large_transactions else 0
    }
    
    # 添加金额分布分析
    amount_distribution = {"ranges": {}}
    
    if valid_transactions:
        min_amount = min(item["amount"] for item in valid_transactions)
        max_amount = max(item["amount"] for item in valid_transactions)
        
        # 根据最大和最小值定义范围
        ranges = []
        if max_amount - min_amount > 100:
            # 创建5个均匀的范围
            step = (max_amount - min_amount) / 5
            for i in range(5):
                low = min_amount + i * step
                high = min_amount + (i + 1) * step if i < 4 else max_amount + 0.01
                ranges.append((low, high))
        else:
            # 使用默认范围
            ranges = [(0, 50), (50, 100), (100, 200), (200, 500), (500, float("inf"))]
        
        # 计算每个范围内的交易数量
        for i, (low, high) in enumerate(ranges):
            range_label = f"{round(low, 2)} - {round(high, 2) if high != float('inf') else '以上'}"
            range_transactions = [item for item in valid_transactions if low <= item["amount"] < high]
            
            amount_distribution["ranges"][range_label] = {
                "count": len(range_transactions),
                "percent": round(len(range_transactions) / len(valid_transactions) * 100, 2),
                "total": round(sum(item["amount"] for item in range_transactions), 2)
            }
    
    # 添加分析结果
    report["threshold_analysis"] = threshold_analysis
    report["amount_distribution"] = amount_distribution
    
    # 提取关键发现
    key_findings = []
    
    # 1. 检查错误率
    if report["data_summary"]["error_rate"] > 5:
        key_findings.append({
            "type": "error_rate",
            "message": f"较高错误率: {report['data_summary']['error_rate']}%的交易存在错误",
            "severity": "high"
        })
    
    # 2. 检查大额交易
    if threshold_analysis["large_transactions_percent"] > 20:
        key_findings.append({
            "type": "large_transactions",
            "message": f"大额交易占比较高: {threshold_analysis['large_transactions_percent']}%的交易超过{amount_threshold}金额",
            "severity": "medium"
        })
    
    # 3. 检查交易类型分布
    for t_type, stats in analyses.get("by_type", {}).items():
        if stats.get("error_count", 0) / stats.get("count", 1) > 0.1:  # 错误率超过10%
            key_findings.append({
                "type": "transaction_type_error",
                "message": f"{t_type}类型交易错误率较高: {round(stats['error_count'] / stats['count'] * 100, 2)}%",
                "severity": "medium"
            })
    
    # 添加关键发现
    report["key_findings"] = key_findings
    
    # 生成建议
    recommendations = []
    
    if report["data_summary"]["error_rate"] > 5:
        recommendations.append("审查交易处理流程，识别和解决导致错误的系统问题")
    
    if threshold_analysis["large_transactions_percent"] > 20:
        recommendations.append(f"考虑对超过{amount_threshold}金额的交易实施额外的审核流程")
    
    for t_type, stats in analyses.get("by_type", {}).items():
        if stats.get("error_count", 0) / stats.get("count", 1) > 0.1:
            recommendations.append(f"优化{t_type}类型交易的处理流程，降低错误率")
    
    report["recommendations"] = recommendations
    
    return report

def generate_log_report(original_data, processed_data, analyses, threshold=None):
    """生成日志数据报告"""
    # 构建报告基本结构
    report = {
        "report_title": "系统日志分析报告",
        "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "total_logs": len(original_data),
            "error_logs": len([item for item in original_data if item["is_error"]]),
            "error_rate": round(len([item for item in original_data if item["is_error"]]) / len(original_data) * 100, 2) if original_data else 0,
            "log_levels": list(set(item["log_level"] for item in original_data)),
            "services": list(set(item["service"] for item in original_data)),
            "time_range": {
                "start": min(item["timestamp"] for item in original_data) if original_data else None,
                "end": max(item["timestamp"] for item in original_data) if original_data else None
            }
        },
        "analyses": analyses
    }
    
    # 构建服务健康分析
    service_health = {}
    
    for service in report["data_summary"]["services"]:
        service_logs = [item for item in processed_data if item["service"] == service]
        error_logs = [item for item in service_logs if item["is_error"]]
        warning_logs = [item for item in service_logs if item["log_level"] == "WARNING"]
        
        # 计算健康评分（简单算法：100 - 10*错误率% - 3*警告率%）
        error_rate = len(error_logs) / len(service_logs) if service_logs else 0
        warning_rate = len(warning_logs) / len(service_logs) if service_logs else 0
        health_score = max(0, min(100, 100 - 10 * (error_rate * 100) - 3 * (warning_rate * 100)))
        
        service_health[service] = {
            "total_logs": len(service_logs),
            "error_logs": len(error_logs),
            "warning_logs": len(warning_logs),
            "error_rate": round(error_rate * 100, 2),
            "warning_rate": round(warning_rate * 100, 2),
            "health_score": round(health_score, 1),
            "status": "正常" if health_score >= 90 else "警告" if health_score >= 70 else "危险",
            "priority_score_avg": sum(item["priority_score"] for item in service_logs) / len(service_logs) if service_logs else 0
        }
    
    # 构建时间趋势分析
    time_trend = []
    for hour, stats in analyses.get("time_series", {}).items():
        error_percent = stats["error"] / stats["total"] * 100 if stats["total"] > 0 else 0
        time_trend.append({
            "hour": hour,
            "total": stats["total"],
            "error": stats["error"],
            "error_percent": round(error_percent, 2),
            "warning": stats["warning"],
            "info": stats["info"]
        })
    
    # 按小时排序
    time_trend.sort(key=lambda x: x["hour"])
    
    # 添加分析结果
    report["service_health"] = service_health
    report["time_trend"] = time_trend
    report["error_patterns"] = analyses.get("error_patterns", [])
    
    # 提取关键发现
    key_findings = []
    
    # 1. 检查总体错误率
    if report["data_summary"]["error_rate"] > 10:
        key_findings.append({
            "type": "error_rate",
            "message": f"系统总体错误率较高: {report['data_summary']['error_rate']}%",
            "severity": "high"
        })
    
    # 2. 检查服务健康状况
    unhealthy_services = [service for service, health in service_health.items() if health["health_score"] < 70]
    if unhealthy_services:
        key_findings.append({
            "type": "service_health",
            "message": f"以下服务健康状况危险: {', '.join(unhealthy_services)}",
            "severity": "high"
        })
    
    warning_services = [service for service, health in service_health.items() if 70 <= health["health_score"] < 90]
    if warning_services:
        key_findings.append({
            "type": "service_health",
            "message": f"以下服务健康状况需要关注: {', '.join(warning_services)}",
            "severity": "medium"
        })
    
    # 3. 检查时间趋势
    if time_trend:
        high_error_hours = [item["hour"] for item in time_trend if item["error_percent"] > 20]
        if high_error_hours:
            key_findings.append({
                "type": "time_trend",
                "message": f"以下时段错误率较高: {', '.join(high_error_hours)}点",
                "severity": "medium"
            })
    
    # 4. 检查常见错误
    if report["error_patterns"] and report["error_patterns"][0]["count"] > 3:
        key_findings.append({
            "type": "error_pattern",
            "message": f"最常见错误: {report['error_patterns'][0]['message']} (出现{report['error_patterns'][0]['count']}次)",
            "severity": "high"
        })
    
    # 添加关键发现
    report["key_findings"] = key_findings
    
    # 生成建议
    recommendations = []
    
    if report["data_summary"]["error_rate"] > 10:
        recommendations.append("优化错误处理流程，降低整体错误率")
    
    for service in unhealthy_services:
        recommendations.append(f"优先修复{service}服务中的问题，当前健康评分: {service_health[service]['health_score']}")
    
    if report["error_patterns"] and report["error_patterns"][0]["count"] > 3:
        recommendations.append(f"解决最常见错误: {report['error_patterns'][0]['message']}")
    
    if high_error_hours:
        recommendations.append(f"调查{', '.join(high_error_hours)}点时段错误率高的原因")
    
    report["recommendations"] = recommendations
    
    return report

def generate_summary_report(report, data_type):
    """生成简洁的总结报告"""
    summary = {
        "report_title": report["report_title"],
        "report_time": report["report_time"],
        "chain_id": report["chain_id"],
        "data_type": data_type,
        "data_summary": report["data_summary"],
        "key_findings": report["key_findings"],
        "recommendations": report["recommendations"]
    }
    
    # 根据数据类型添加关键分析
    if data_type == "sensor":
        # 添加传感器类型统计
        summary["sensor_stats"] = {}
        for sensor_type, analysis in report["analyses"].items():
            summary["sensor_stats"][sensor_type] = {
                "count": analysis["total_count"],
                "error_rate": analysis["error_rate"],
                "avg_value": analysis["statistics"]["mean"] if "statistics" in analysis and "mean" in analysis["statistics"] else None,
                "unit": analysis["unit"]
            }
        
        # 添加异常统计
        summary["anomaly_count"] = report["anomaly_count"]
        summary["anomaly_rate"] = report["anomaly_rate"]
        
    elif data_type == "transaction":
        # 添加交易统计
        summary["transaction_stats"] = {
            "total_amount": report["analyses"]["total_amount"],
            "avg_amount": report["analyses"]["avg_amount"],
            "large_transactions": {
                "count": report["threshold_analysis"]["large_transactions_count"],
                "percent": report["threshold_analysis"]["large_transactions_percent"],
                "threshold": report["threshold_analysis"]["threshold"]
            }
        }
        
        # 添加交易类型统计
        summary["transaction_types"] = {}
        for t_type, stats in report["analyses"]["by_type"].items():
            summary["transaction_types"][t_type] = {
                "count": stats["count"],
                "error_rate": round(stats["error_count"] / stats["count"] * 100, 2) if stats["count"] > 0 else 0,
                "avg_amount": stats["avg_amount"] if "avg_amount" in stats else None
            }
        
    elif data_type == "log":
        # 添加日志统计
        summary["log_stats"] = {
            "by_level": report["analyses"]["by_level"],
            "error_rate": report["data_summary"]["error_rate"]
        }
        
        # 添加服务健康状况
        summary["service_health"] = {}
        for service, health in report["service_health"].items():
            summary["service_health"][service] = {
                "health_score": health["health_score"],
                "status": health["status"],
                "error_rate": health["error_rate"]
            }
        
        # 添加最常见错误
        if report["error_patterns"]:
            summary["top_errors"] = report["error_patterns"][:3]  # 只包含前3个
    
    return summary

def generate_visualization_code(data_type, processed_data, analyses):
    """生成数据可视化代码"""
    visualization = {
        "description": "以下是数据可视化代码，可以复制到HTML文件中使用或在Jupyter Notebook中执行",
        "dependencies": [
            "https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js",
            "https://cdn.jsdelivr.net/npm/echarts@5.3.2/dist/echarts.min.js"
        ],
        "html_template": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>数据分析可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.3.2/dist/echarts.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chart-container { width: 100%; height: 400px; margin-bottom: 30px; }
        .card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card-title { font-size: 18px; font-weight: bold; margin-bottom: 15px; }
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) { .grid-container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <h1>数据分析可视化报告</h1>
    <div class="card">
        <div class="card-title">数据概览</div>
        <div id="summary-container"></div>
    </div>
    
    <div class="grid-container">
        <div class="card">
            <div class="card-title">主要指标</div>
            <div class="chart-container">
                <canvas id="main-chart"></canvas>
            </div>
        </div>
        <div class="card">
            <div class="card-title">数据分布</div>
            <div class="chart-container">
                <div id="distribution-chart"></div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-title">时间趋势</div>
        <div class="chart-container">
            <div id="trend-chart"></div>
        </div>
    </div>
    
    <script>
        // 这里将插入数据和可视化代码
        const data = DATA_PLACEHOLDER;
        
        // 填充概览信息
        function renderSummary() {
            const summaryEl = document.getElementById('summary-container');
            let summaryHTML = '<ul>';
            
            if (data.type === 'sensor') {
                summaryHTML += `<li>总传感器数: ${data.total_sensors}</li>`;
                summaryHTML += `<li>总读数: ${data.total_readings}</li>`;
                summaryHTML += `<li>错误率: ${data.error_rate}%</li>`;
                summaryHTML += `<li>异常值: ${data.anomaly_count}个 (${data.anomaly_rate}%)</li>`;
            } else if (data.type === 'transaction') {
                summaryHTML += `<li>总交易数: ${data.total_transactions}</li>`;
                summaryHTML += `<li>总金额: ${data.total_amount}</li>`;
                summaryHTML += `<li>平均金额: ${data.avg_amount}</li>`;
                summaryHTML += `<li>错误率: ${data.error_rate}%</li>`;
            } else if (data.type === 'log') {
                summaryHTML += `<li>总日志数: ${data.total_logs}</li>`;
                summaryHTML += `<li>错误日志: ${data.error_logs} (${data.error_rate}%)</li>`;
                summaryHTML += `<li>服务数: ${data.services.length}</li>`;
                summaryHTML += `<li>危险状态服务: ${data.critical_services || 0}</li>`;
            }
            
            summaryHTML += '</ul>';
            summaryEl.innerHTML = summaryHTML;
        }
        
        // 渲染主图表
        function renderMainChart() {
            const ctx = document.getElementById('main-chart').getContext('2d');
            let chartData, options;
            
            if (data.type === 'sensor') {
                chartData = {
                    labels: Object.keys(data.sensor_stats),
                    datasets: [{
                        label: '平均值',
                        data: Object.values(data.sensor_stats).map(s => s.avg_value),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                };
                options = {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: '各类传感器平均值' }
                    }
                };
            } else if (data.type === 'transaction') {
                chartData = {
                    labels: Object.keys(data.transaction_types),
                    datasets: [{
                        label: '交易数',
                        data: Object.values(data.transaction_types).map(t => t.count),
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                };
                options = {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        title: { display: true, text: '各类交易数量' }
                    }
                };
            } else if (data.type === 'log') {
                chartData = {
                    labels: Object.keys(data.by_level),
                    datasets: [{
                        label: '日志数',
                        data: Object.values(data.by_level),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.5)', 
                            'rgba(255, 159, 64, 0.5)',
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(75, 192, 192, 0.5)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                };
                options = {
                    responsive: true,
                    plugins: {
                        legend: { position: 'right' },
                        title: { display: true, text: '日志级别分布' }
                    }
                };
            }
            
            new Chart(ctx, {
                type: data.type === 'log' ? 'pie' : 'bar',
                data: chartData,
                options: options
            });
        }
        
        // 渲染分布图
        function renderDistributionChart() {
            const chartDom = document.getElementById('distribution-chart');
            const myChart = echarts.init(chartDom);
            let option;
            
            if (data.type === 'sensor') {
                // 使用箱线图展示传感器数据分布
                option = {
                    title: { text: '传感器数据分布' },
                    dataset: [
                        {
                            source: data.distributions || []
                        }
                    ],
                    tooltip: { trigger: 'item' },
                    xAxis: { type: 'category' },
                    yAxis: { type: 'value' },
                    series: [
                        {
                            name: '数据分布',
                            type: 'boxplot',
                            datasetIndex: 0
                        }
                    ]
                };
            } else if (data.type === 'transaction') {
                // 使用饼图展示交易金额分布
                option = {
                    title: { text: '交易金额分布' },
                    tooltip: { trigger: 'item' },
                    legend: { orient: 'vertical', left: 'left' },
                    series: [
                        {
                            name: '金额分布',
                            type: 'pie',
                            radius: '60%',
                            data: Object.keys(data.amount_distribution || {}).map(key => ({
                                name: key,
                                value: data.amount_distribution[key].count
                            })),
                            emphasis: {
                                itemStyle: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                };
            } else if (data.type === 'log') {
                // 使用条形图展示服务健康状况
                option = {
                    title: { text: '服务健康状况' },
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['健康评分', '错误率'] },
                    xAxis: { 
                        type: 'value', 
                        splitLine: { show: false } 
                    },
                    yAxis: { 
                        type: 'category', 
                        data: Object.keys(data.service_health || {}) 
                    },
                    series: [
                        {
                            name: '健康评分',
                            type: 'bar',
                            data: Object.values(data.service_health || {}).map(s => s.health_score)
                        },
                        {
                            name: '错误率',
                            type: 'bar',
                            data: Object.values(data.service_health || {}).map(s => s.error_rate)
                        }
                    ]
                };
            }
            
            myChart.setOption(option);
        }
        
        // 渲染趋势图
        function renderTrendChart() {
            const chartDom = document.getElementById('trend-chart');
            const myChart = echarts.init(chartDom);
            let option;
            
            if (data.time_trend) {
                option = {
                    title: { text: '时间趋势' },
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['总数', '错误数', '错误率(%)'] },
                    xAxis: { 
                        type: 'category', 
                        data: data.time_trend.map(t => t.hour) 
                    },
                    yAxis: [
                        {
                            type: 'value',
                            name: '数量',
                            position: 'left'
                        },
                        {
                            type: 'value',
                            name: '百分比',
                            position: 'right',
                            min: 0,
                            max: 100
                        }
                    ],
                    series: [
                        {
                            name: '总数',
                            type: 'bar',
                            stack: 'total',
                            data: data.time_trend.map(t => t.total)
                        },
                        {
                            name: '错误数',
                            type: 'bar',
                            stack: 'error',
                            data: data.time_trend.map(t => t.error)
                        },
                        {
                            name: '错误率(%)',
                            type: 'line',
                            yAxisIndex: 1,
                            data: data.time_trend.map(t => t.error_percent)
                        }
                    ]
                };
            } else {
                option = {
                    title: { text: '无时间趋势数据' },
                    xAxis: { type: 'category', data: [] },
                    yAxis: { type: 'value' },
                    series: [{ type: 'line', data: [] }]
                };
            }
            
            myChart.setOption(option);
        }
        
        // 初始化所有图表
        renderSummary();
        renderMainChart();
        renderDistributionChart();
        renderTrendChart();
    </script>
</body>
</html>
"""
    }
    
    # 根据数据类型准备示例数据
    if data_type == "sensor":
        # 构建传感器可视化数据
        visualization_data = {
            "type": "sensor",
            "total_sensors": len(set(item["sensor_type"] for item in processed_data)),
            "total_readings": len(processed_data),
            "error_rate": round(len([item for item in processed_data if item["is_error"]]) / len(processed_data) * 100, 2) if processed_data else 0,
            "anomaly_count": len([item for item in processed_data if item.get("is_anomaly")]),
            "anomaly_rate": round(len([item for item in processed_data if item.get("is_anomaly")]) / len([item for item in processed_data if not item["is_error"]]) * 100, 2) if processed_data else 0,
            "sensor_stats": {}
        }
        
        # 添加各类传感器统计
        for sensor_type, analysis in analyses.items():
            visualization_data["sensor_stats"][sensor_type] = {
                "avg_value": analysis["statistics"]["mean"] if "statistics" in analysis and "mean" in analysis["statistics"] else 0,
                "min_value": analysis["statistics"]["min"] if "statistics" in analysis and "min" in analysis["statistics"] else 0,
                "max_value": analysis["statistics"]["max"] if "statistics" in analysis and "max" in analysis["statistics"] else 0,
                "std_dev": analysis["statistics"]["stddev"] if "statistics" in analysis and "stddev" in analysis["statistics"] else 0,
                "unit": analysis["unit"] if "unit" in analysis else ""
            }
            
    elif data_type == "transaction":
        # 构建交易可视化数据
        visualization_data = {
            "type": "transaction",
            "total_transactions": len(processed_data),
            "total_amount": round(sum(item["amount"] for item in processed_data if not item["is_error"]), 2),
            "avg_amount": round(sum(item["amount"] for item in processed_data if not item["is_error"]) / len([item for item in processed_data if not item["is_error"]]), 2) if processed_data else 0,
            "error_rate": round(len([item for item in processed_data if item["is_error"]]) / len(processed_data) * 100, 2) if processed_data else 0,
            "transaction_types": {},
            "amount_distribution": {}
        }
        
        # 添加交易类型统计
        for t_type, stats in analyses.get("by_type", {}).items():
            visualization_data["transaction_types"][t_type] = {
                "count": stats["count"],
                "error_count": stats.get("error_count", 0),
                "avg_amount": round(stats.get("avg_amount", 0), 2)
            }
            
        # 添加金额分布
        amount_distribution = analyses.get("amount_distribution", {}).get("ranges", {})
        for range_name, range_stats in amount_distribution.items():
            visualization_data["amount_distribution"][range_name] = {
                "count": range_stats["count"],
                "percent": range_stats["percent"],
                "total": range_stats["total"]
            }
            
    elif data_type == "log":
        # 构建日志可视化数据
        visualization_data = {
            "type": "log",
            "total_logs": len(processed_data),
            "error_logs": len([item for item in processed_data if item["is_error"]]),
            "error_rate": round(len([item for item in processed_data if item["is_error"]]) / len(processed_data) * 100, 2) if processed_data else 0,
            "services": list(set(item["service"] for item in processed_data)),
            "by_level": analyses.get("by_level", {}),
            "service_health": {},
            "time_trend": []
        }
        
        # 服务健康状况
        for service, health in analyses.get("service_health", {}).items():
            visualization_data["service_health"][service] = {
                "health_score": health["health_score"],
                "error_rate": health["error_rate"],
                "status": health["status"]
            }
            
        # 时间趋势
        for item in analyses.get("time_trend", []):
            visualization_data["time_trend"].append({
                "hour": item["hour"],
                "total": item["total"],
                "error": item["error"],
                "error_percent": item["error_percent"]
            })
    
    # 添加JavaScript数据替换部分
    js_data = json.dumps(visualization_data, ensure_ascii=False, indent=2)
    visualization["js_data"] = js_data
    
    # 替换模板中的占位符
    visualization["html_code"] = visualization["html_template"].replace("DATA_PLACEHOLDER", js_data)
    
    return visualization
