#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立的邮件发送测试脚本
不依赖项目中的其他模块，可以单独运行
"""
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    """发送测试邮件"""
    # 邮件配置（使用与EmailService相同的配置）
    smtp_server = "smtp.163.com"
    smtp_port = 465  # 使用SSL端口
    username = "18345374903@163.com"      # 发件人邮箱
    password = "GHTbrMYUhgSBZVtg"                # 授权码
    sender = "18345374903@163.com"        # 发件人邮箱
    recipient = "zhuyuanhui20023@163.com" # 收件人邮箱
    
    # 打印配置信息（密码除外）
    print(f"SMTP服务器: {smtp_server}")
    print(f"SMTP端口: {smtp_port}")
    print(f"用户名: {username}")
    print(f"发件人: {sender}")
    print(f"收件人: {recipient}")
    
    # 当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建测试邮件内容
    subject = f"独立测试邮件 - {current_time}"
    body = f"""这是一封独立测试邮件，用于验证邮件发送功能是否正常工作。

发送时间: {current_time}
发送服务器: {smtp_server}:{smtp_port}
发件人: {sender}

如果您收到这封邮件，说明邮件发送功能正常工作。
"""
    
    try:
        print("正在发送测试邮件...")
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 连接SMTP服务器并发送邮件
        # 使用SSL连接（适用于端口465）
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)
            server.sendmail(sender, recipient, msg.as_string())
        
        print("邮件发送成功！")
        print(f"收件人: {recipient}")
        print(f"主题: {subject}")
        return True
        
    except Exception as e:
        print(f"发送邮件时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_email()
