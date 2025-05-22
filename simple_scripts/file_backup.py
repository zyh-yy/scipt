#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件备份脚本

这个脚本用于创建指定目录的备份。它会将源目录中的所有文件复制到目标目录，
并添加时间戳，以便于区分不同时间的备份。

用法:
    python file_backup.py [源目录] [目标目录]

示例:
    python file_backup.py C:/项目文件 D:/备份
"""

import os
import sys
import shutil
import datetime
import argparse


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="备份指定目录下的文件")
    parser.add_argument("source", help="源目录路径")
    parser.add_argument("destination", help="目标目录路径")
    parser.add_argument("-i", "--ignore", nargs="+", default=[],
                        help="要忽略的文件或目录名列表")
    return parser.parse_args()


def create_backup(source_dir, dest_dir, ignore_list):
    """
    创建目录备份
    
    参数:
        source_dir (str): 源目录路径
        dest_dir (str): 目标目录路径
        ignore_list (list): 要忽略的文件或目录名列表
    
    返回:
        str: 备份目录路径
    """
    # 验证源目录存在
    if not os.path.exists(source_dir):
        print(f"错误: 源目录 '{source_dir}' 不存在!")
        sys.exit(1)
        
    # 创建带时间戳的备份目录名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(dest_dir, f"backup_{timestamp}")
    
    # 确保目标目录存在
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # 创建备份目录
    os.makedirs(backup_dir)
    
    # 复制文件
    files_copied = 0
    total_size = 0
    
    print(f"开始备份 '{source_dir}' 到 '{backup_dir}'...")
    
    for root, dirs, files in os.walk(source_dir):
        # 移除忽略的目录
        for ignore_item in ignore_list:
            if ignore_item in dirs:
                dirs.remove(ignore_item)
        
        # 为目标创建相应的目录结构
        rel_path = os.path.relpath(root, source_dir)
        if rel_path != ".":
            target_dir = os.path.join(backup_dir, rel_path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
        else:
            target_dir = backup_dir
        
        # 复制文件
        for file in files:
            # 跳过忽略的文件
            if file in ignore_list:
                continue
                
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            try:
                shutil.copy2(source_file, target_file)
                file_size = os.path.getsize(source_file)
                total_size += file_size
                files_copied += 1
                print(f"已复制: {source_file} -> {target_file}")
            except Exception as e:
                print(f"复制 '{source_file}' 时出错: {e}")
    
    # 显示备份统计信息
    print("\n备份完成!")
    print(f"文件总数: {files_copied}")
    print(f"总大小: {total_size / (1024*1024):.2f} MB")
    print(f"备份目录: {backup_dir}")
    
    return backup_dir


def main():
    """主函数"""
    args = parse_arguments()
    create_backup(args.source, args.destination, args.ignore)


if __name__ == "__main__":
    main()
