#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮箱发送功能测试脚本
仅用于测试邮件发送功能，不依赖其他系统功能
"""
import os
import sys
import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入邮件服务
from backend.services.email_service import EmailService

def main():
    """测试邮件发送功能"""
    print("开始测试邮件发送功能...")
    
    # 创建邮件服务实例
    email_service = EmailService()
    
    # 打印当前配置信息（密码除外）
    print(f"SMTP服务器: {email_service.smtp_server}")
    print(f"SMTP端口: {email_service.smtp_port}")
    print(f"用户名: {email_service.username}")
    print(f"默认发件人: {email_service.default_sender}")
    
    # 当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建测试邮件内容
    subject = f"测试邮件 - {current_time}"
    body = f"""这是一封测试邮件，用于验证邮件发送功能是否正常工作。

发送时间: {current_time}
发送服务器: {email_service.smtp_server}:{email_service.smtp_port}
发件人: {email_service.default_sender}

如果您收到这封邮件，说明邮件发送功能正常工作。
"""
    
    try:
        print("正在发送测试邮件...")
        # 使用默认收件人发送测试邮件
        success = email_service.send_email(
            recipients=None,  # 使用默认收件人
            subject=subject,
            body=body,
            html=False
        )
        
        # 输出结果
        if success:
            print("邮件发送成功！")
            print(f"收件人: {email_service.DEFAULT_RECIPIENT}")
            print(f"主题: {subject}")
            return 0
        else:
            print("邮件发送失败！")
            return 1
            
    except Exception as e:
        print(f"发送邮件时发生错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
