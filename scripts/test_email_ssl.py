#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用SSL和EmailMessage发送邮件的测试脚本
参考提供的示例代码实现
"""
import smtplib
import ssl
import datetime
from email.message import EmailMessage

def send_test_email():
    """使用SSL和EmailMessage发送测试邮件"""
    # 邮件配置
    EMAIL_ADDRESS = "18345374903@163.com"     # 发件人邮箱
    EMAIL_PASSWORD = "GHTbrMYUhgSBZVtg"              # 授权码
    RECIPIENT = "zhuyuanhui2002@163.com"     # 收件人邮箱
    
    # 打印配置信息（密码除外）
    print(f"发件人: {EMAIL_ADDRESS}")
    print(f"收件人: {RECIPIENT}")
    
    # 当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建邮件
    subject = f"使用SSL的测试邮件 - {current_time}"
    body = f"""这是一封使用SSL和EmailMessage发送的测试邮件。

发送时间: {current_time}
发送服务器: smtp.163.com:465
发件人: {EMAIL_ADDRESS}

如果您收到这封邮件，说明邮件发送功能正常工作。
"""
    
    # 使用EmailMessage创建消息
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT
    msg.set_content(body)
    
    try:
        print("正在发送测试邮件...")
        
        # 创建SSL安全上下文
        context = ssl.create_default_context()
        
        # 使用SSL连接发送邮件
        with smtplib.SMTP_SSL("smtp.163.com", 465, context=context) as smtp:
            # 登录
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            
            # 发送邮件
            smtp.send_message(msg)
        
        print("邮件发送成功！")
        print(f"收件人: {RECIPIENT}")
        print(f"主题: {subject}")
        return True
        
    except Exception as e:
        print(f"发送邮件时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_email()
