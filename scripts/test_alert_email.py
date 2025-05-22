#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
告警邮件发送测试脚本
直接测试系统的告警邮件发送功能
"""
import os
import sys
import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.execution import ExecutionHistory, AlertConfig, AlertHandler
from backend.services.email_service import EmailService
from backend.config import logger

def main():
    """测试告警邮件发送功能"""
    try:
        logger.info("开始测试告警邮件发送功能")
        
        # 检查是否已经创建了测试告警配置
        alert_configs = AlertConfig.get_all()
        test_config = None
        
        for config in alert_configs:
            if config['name'] == '测试告警配置':
                test_config = config
                logger.info(f"找到现有测试告警配置: ID={config['id']}")
                break
        
        # 如果没有找到测试配置，创建一个新的
        if not test_config:
            logger.info("创建新的测试告警配置")
            config_id = AlertConfig.add(
                name='测试告警配置',
                description='用于测试邮件告警功能',
                alert_type='execution_status',
                condition_type='equals',
                condition_value='failed',
                notification_type='email',
                notification_config={'recipients': []}  # 使用默认收件人
            )
            
            if not config_id:
                logger.error("创建告警配置失败")
                return 1
            
            test_config = AlertConfig.get(config_id)
            logger.info(f"成功创建测试告警配置: ID={config_id}")
        
        # 创建一个执行历史记录
        logger.info("创建测试执行历史记录")
        history_id = ExecutionHistory.add(
            script_id=999,  # 使用一个假的脚本ID
            status="running",
            params={"test": True},
            output="测试输出"
        )
        
        if not history_id:
            logger.error("创建执行历史记录失败")
            return 1
        
        logger.info(f"成功创建测试执行历史记录: ID={history_id}")
        
        # 更新执行历史为失败状态
        logger.info("更新执行历史记录为失败状态")
        success = ExecutionHistory.update(
            history_id=history_id,
            status="failed",
            error="这是一个测试错误消息，用于触发告警邮件"
        )
        
        if not success:
            logger.error("更新执行历史记录失败")
            return 1
        
        logger.info(f"成功将执行历史记录更新为失败状态")
        
        # 手动测试发送邮件
        logger.info("手动测试邮件服务")
        email_service = EmailService()
        email_result = email_service.send_email(
            subject="手动测试邮件",
            body="这是一封直接通过EmailService发送的测试邮件。\n如果您收到这封邮件，说明邮件服务配置正确。",
            html=False
        )
        
        logger.info(f"手动发送邮件结果: {'成功' if email_result else '失败'}")
        
        # 手动触发告警处理
        logger.info("直接触发告警处理器")
        execution = ExecutionHistory.get(history_id)
        AlertHandler.trigger_alert(test_config, execution, "failed", "这是一个手动触发的测试告警")
        
        logger.info("告警测试完成")
        return 0
        
    except Exception as e:
        logger.error(f"测试过程中发生异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
