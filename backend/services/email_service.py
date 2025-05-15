# -*- coding: utf-8 -*-
"""
邮件服务
用于发送邮件通知
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import logger

class EmailService:
    """邮件服务类"""
    
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None, default_sender=None):
        """
        初始化邮件服务
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
            username: SMTP用户名
            password: SMTP密码
            default_sender: 默认发件人
        """
        # 如果未提供参数，尝试从环境变量获取
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 587))
        self.username = username or os.environ.get('SMTP_USERNAME')
        self.password = password or os.environ.get('SMTP_PASSWORD')
        self.default_sender = default_sender or os.environ.get('DEFAULT_SENDER_EMAIL')
        
        if not all([self.smtp_server, self.smtp_port, self.username, self.password, self.default_sender]):
            logger.warning("邮件服务初始化失败: 缺少必要的SMTP配置")
    
    def send_email(self, recipients, subject, body, sender=None, html=False):
        """
        发送邮件
        
        Args:
            recipients: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            sender: 发件人，如果未提供则使用默认发件人
            html: 是否为HTML格式邮件
            
        Returns:
            bool: 是否发送成功
        """
        try:
            if not all([self.smtp_server, self.smtp_port, self.username, self.password]):
                logger.error("发送邮件失败: 缺少SMTP配置")
                return False
            
            sender = sender or self.default_sender
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = sender
            
            # 处理收件人列表
            if isinstance(recipients, str):
                recipients = [recipients]
            
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # 添加邮件正文
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                # 大多数SMTP服务器要求安全连接
                if self.smtp_port in [587, 25]:
                    server.starttls()
                    server.ehlo()
                
                server.login(self.username, self.password)
                server.sendmail(sender, recipients, msg.as_string())
            
            logger.info(f"邮件发送成功: {subject} 发送给 {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    @staticmethod
    def test_connection(smtp_server, smtp_port, username, password):
        """
        测试SMTP连接
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
            username: SMTP用户名
            password: SMTP密码
            
        Returns:
            tuple: (success, message)
        """
        try:
            # 连接SMTP服务器
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                # 大多数SMTP服务器要求安全连接
                if smtp_port in [587, 25]:
                    server.starttls()
                    server.ehlo()
                
                server.login(username, password)
            
            return True, "SMTP连接测试成功"
            
        except Exception as e:
            return False, f"SMTP连接测试失败: {str(e)}"
