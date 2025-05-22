#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
告警通知测试脚本
此脚本故意产生错误，用于测试系统的告警通知功能
"""
import sys
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """主函数，故意产生错误"""
    logger.info("开始执行告警测试脚本")
    
    try:
        # 暂停2秒，让脚本执行时间更明显
        logger.info("脚本执行中...")
        time.sleep(2)
        
        # 故意产生错误 - 除以零
        logger.info("即将产生错误...")
        result = 100 / 0
        
        # 这段代码永远不会执行
        print("如果你看到这条消息，说明脚本没有产生预期的错误")
        return 0
        
    except Exception as e:
        # 记录错误
        logger.error(f"发生错误: {str(e)}")
        # 确保错误传递给执行系统
        raise

if __name__ == "__main__":
    sys.exit(main())
