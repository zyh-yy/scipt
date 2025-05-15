#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件生成器脚本
根据指定的参数生成文件
参数说明：
- filename: 要生成的文件名（必填）
- content: 文件内容（必填）
- format: 格式化类型（选填，默认为'plain'，可选值：'plain', 'json', 'html', 'csv', 'xml'）
- metadata: 元数据（选填，JSON对象）
"""
import os
import sys
import json
import datetime
import csv
import io
from xml.dom.minidom import parseString

def format_content(content, format_type, metadata=None):
    """根据指定格式格式化内容"""
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 准备元数据
        meta = metadata or {}
        meta["generated_time"] = now
        
        # 根据格式类型格式化内容
        if format_type == "plain":
            # 纯文本格式，添加元数据作为注释
            formatted = f"# 生成时间: {now}\n"
            for k, v in meta.items():
                if k != "generated_time":
                    formatted += f"# {k}: {v}\n"
            formatted += "\n" + content
            
        elif format_type == "json":
            # JSON格式
            data = {
                "content": content,
                "metadata": meta
            }
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            
        elif format_type == "html":
            # HTML格式
            meta_html = ""
            for k, v in meta.items():
                meta_html += f"<!-- {k}: {v} -->\n"
            
            formatted = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>生成的文件</title>
    {meta_html}
</head>
<body>
    <pre>{content}</pre>
</body>
</html>"""
            
        elif format_type == "csv":
            # CSV格式
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入元数据作为注释行
            for k, v in meta.items():
                writer.writerow([f"# {k}", v])
            
            # 将内容按行分割并写入CSV
            for line in content.split("\n"):
                if line.strip():
                    fields = line.split(",")
                    writer.writerow(fields)
                    
            formatted = output.getvalue()
            output.close()
            
        elif format_type == "xml":
            # XML格式
            meta_xml = "".join([f'<meta name="{k}">{v}</meta>' for k, v in meta.items()])
            
            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<document>
    <metadata>
        {meta_xml}
    </metadata>
    <content><![CDATA[{content}]]></content>
</document>"""
            
            # 美化XML
            try:
                parsed_xml = parseString(xml)
                formatted = parsed_xml.toprettyxml(indent="  ")
            except:
                formatted = xml
                
        else:
            # 默认为纯文本
            formatted = content
            
        return True, formatted, None
    except Exception as e:
        return False, None, str(e)

def create_file(filename, content):
    """创建文件"""
    try:
        # 确保目录存在
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        # 获取文件信息
        file_info = {
            "filename": filename,
            "size_bytes": os.path.getsize(filename),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "absolute_path": os.path.abspath(filename)
        }
        
        return True, file_info, None
    except Exception as e:
        return False, None, str(e)

def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少参数文件路径"}))
        return 1
        
    params_file = sys.argv[1]
    
    # 读取参数文件
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"读取参数文件失败: {str(e)}"}))
        return 1
    
    # 检查必填参数
    if 'filename' not in params:
        print(json.dumps({"error": "缺少必填参数: filename"}))
        return 1
        
    if 'content' not in params:
        print(json.dumps({"error": "缺少必填参数: content"}))
        return 1
    
    # 获取参数值
    filename = params.get('filename')
    content = params.get('content')
    format_type = params.get('format', 'plain')
    metadata = params.get('metadata', {})
    
    # 格式化内容
    success, formatted_content, error = format_content(content, format_type, metadata)
    if not success:
        print(json.dumps({"error": f"格式化内容失败: {error}"}))
        return 1
    
    # 创建文件
    success, file_info, error = create_file(filename, formatted_content)
    if not success:
        print(json.dumps({"error": f"创建文件失败: {error}"}))
        return 1
    
    # 输出结果
    result = {
        "success": True,
        "message": f"文件已成功生成",
        "file_info": file_info,
        "format": format_type
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
