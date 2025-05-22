# -*- coding: utf-8 -*-
"""
邮件服务
用于发送邮件通知
"""
import os
import sys
import smtplib
import ssl
import logging
from email.message import EmailMessage

# 尝试直接导入，如果失败则设置一个基本的日志记录器
try:
    from config import logger
except ImportError:
    # 创建一个基本的日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    # 默认的固定SMTP配置
    DEFAULT_SMTP_SERVER = "smtp.163.com"
    DEFAULT_SMTP_PORT = 465  # 使用SSL端口
    DEFAULT_USERNAME = "18345374903@163.com"  # 发件人邮箱
    DEFAULT_PASSWORD = "GHTbrMYUhgSBZVtg"            # 授权码
    DEFAULT_SENDER = "18345374903@163.com"    # 发件人邮箱
    DEFAULT_RECIPIENT = "zhuyuanhui20023@163.com" # 收件人邮箱
    
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
        # 优先使用参数值，其次使用环境变量，最后使用固定配置
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER') or self.DEFAULT_SMTP_SERVER
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', 465)) or self.DEFAULT_SMTP_PORT
        self.username = username or os.environ.get('SMTP_USERNAME') or self.DEFAULT_USERNAME
        self.password = password or os.environ.get('SMTP_PASSWORD') or self.DEFAULT_PASSWORD
        self.default_sender = default_sender or os.environ.get('DEFAULT_SENDER_EMAIL') or self.DEFAULT_SENDER
    
    def send_email(self, recipients=None, subject="系统通知", body="这是一条系统自动发送的通知", sender=None, html=False):
        """
        发送邮件
        
        Args:
            recipients: 收件人列表，如果未提供则使用默认收件人
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
            
            # 如果未提供收件人，使用默认收件人
            if recipients is None:
                recipients = [self.DEFAULT_RECIPIENT]
            elif isinstance(recipients, str):
                recipients = [recipients]
            
            # 创建EmailMessage对象
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            
            # 设置邮件内容
            if html:
                msg.set_content(body, subtype='html')
            else:
                msg.set_content(body)
            
            # 创建SSL安全上下文
            context = ssl.create_default_context()
            
            # 根据端口选择连接方式
            if self.smtp_port == 465:
                # 使用SSL连接
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                # 使用普通SMTP或TLS
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.ehlo()
                    # 对于TLS端口，启用TLS
                    if self.smtp_port in [587, 25]:
                        server.starttls(context=context)
                        server.ehlo()
                    
                    server.login(self.username, self.password)
                    server.send_message(msg)
            
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
            # 创建SSL安全上下文
            context = ssl.create_default_context()
            
            # 根据端口选择连接方式
            if smtp_port == 465:
                # 使用SSL连接
                with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                    server.login(username, password)
            else:
                # 使用普通SMTP或TLS
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    # 对于TLS端口，启用TLS
                    if smtp_port in [587, 25]:
                        server.starttls(context=context)
                        server.ehlo()
                    
                    server.login(username, password)
            
            return True, "SMTP连接测试成功"
            
        except Exception as e:
            return False, f"SMTP连接测试失败: {str(e)}"
