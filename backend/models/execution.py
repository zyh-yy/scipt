# -*- coding: utf-8 -*-
"""
执行历史模型模块
定义执行历史相关数据库模型和操作
"""
import datetime
import json
import time
import os
import sys
from .base import DBManager

# Use the same approach for importing config as in base.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import logger

class AlertHandler:
    """告警处理器类"""
    
    @staticmethod
    def check_alerts(execution_id, status, error=None):
        """检查是否需要触发告警"""
        try:
            # 获取执行记录详情
            execution = ExecutionHistory.get(execution_id)
            if not execution:
                return False
            
            # 获取所有激活的告警配置
            alert_configs = AlertConfig.get_all(is_active=1)
            
            for config in alert_configs:
                # 根据不同的告警类型和条件检查是否需要触发
                if config['alert_type'] == 'execution_status':
                    # 执行状态告警
                    if config['condition_type'] == 'equals' and config['condition_value'] == status:
                        AlertHandler.trigger_alert(config, execution, status, error)
                    elif config['condition_type'] == 'contains_error' and status == 'failed' and error:
                        AlertHandler.trigger_alert(config, execution, status, error)
                
                elif config['alert_type'] == 'execution_time':
                    # 执行时间告警
                    if execution.get('execution_time') and float(execution['execution_time']) > float(config['condition_value']):
                        AlertHandler.trigger_alert(config, execution, status, f"执行时间 {execution['execution_time']} 秒超过阈值 {config['condition_value']} 秒")
            
            return True
        except Exception as e:
            logger.error(f"检查告警失败: {str(e)}")
            return False
    
    @staticmethod
    def trigger_alert(alert_config, execution, status, message=None):
        """触发告警通知"""
        try:
            # 生成告警消息内容
            if not message:
                message = f"脚本执行{'成功' if status == 'completed' else '失败'}"
            
            if execution.get('script_id'):
                subject = f"脚本执行{status}告警"
                content = f"脚本ID: {execution['script_id']}\n"
            elif execution.get('chain_id'):
                subject = f"脚本链执行{status}告警"
                content = f"脚本链ID: {execution['chain_id']}\n"
            else:
                subject = f"执行{status}告警"
                content = ""
            
            content += f"执行ID: {execution['id']}\n"
            content += f"状态: {status}\n"
            content += f"开始时间: {execution['start_time']}\n"
            if execution.get('end_time'):
                content += f"结束时间: {execution['end_time']}\n"
            if execution.get('execution_time'):
                content += f"执行时间: {execution['execution_time']} 秒\n"
            content += f"消息: {message}\n"
            
            # 根据通知类型发送告警
            if alert_config['notification_type'] == 'email':
                # 发送邮件告警
                notification_config = alert_config['notification_config']
                recipients = notification_config.get('recipients', [])
                
                from services.email_service import EmailService
                email_service = EmailService()
                success = email_service.send_email(recipients, subject, content)
                
                # 记录告警历史
                status = "sent" if success else "failed"
                AlertHistory.add(alert_config['id'], execution['id'], status, message)
                
                return success
            
            # 添加更多通知类型支持
            
            return False
        except Exception as e:
            logger.error(f"触发告警失败: {str(e)}")
            return False


class ExecutionHistory:
    """执行历史模型类"""
    
    @staticmethod
    def add(script_id=None, chain_id=None, status="running", params=None, output=None, error=None):
        """添加执行历史记录"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            params_json = json.dumps(params) if params else None
            
            cursor.execute('''
            INSERT INTO execution_history
            (script_id, chain_id, status, start_time, params, output, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (script_id, chain_id, status, now, params_json, output, error))
            
            history_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加执行历史记录成功: 脚本ID {script_id}, 链ID {chain_id}")
            return history_id
        except Exception as e:
            logger.error(f"添加执行历史记录失败: {str(e)}")
            return None
    
    @staticmethod
    def update(history_id, status=None, output=None, error=None):
        """更新执行历史记录"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前记录
            cursor.execute("SELECT * FROM execution_history WHERE id = ?", (history_id,))
            history = cursor.fetchone()
            
            if not history:
                logger.error(f"更新执行历史记录失败: 记录ID {history_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_status = status if status is not None else history['status']
            update_output = output if output is not None else history['output']
            update_error = error if error is not None else history['error']
            
            # 如果状态是已完成或失败，更新结束时间
            end_time = None
            execution_time = None
            if status in ["completed", "failed"]:
                end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 计算执行时间（秒）
                if history['start_time']:
                    start_dt = datetime.datetime.strptime(history['start_time'], '%Y-%m-%d %H:%M:%S')
                    end_dt = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
                    execution_time = (end_dt - start_dt).total_seconds()
                
                cursor.execute('''
                UPDATE execution_history
                SET status = ?, output = ?, error = ?, end_time = ?, execution_time = ?
                WHERE id = ?
                ''', (update_status, update_output, update_error, end_time, execution_time, history_id))
            else:
                cursor.execute('''
                UPDATE execution_history
                SET status = ?, output = ?, error = ?
                WHERE id = ?
                ''', (update_status, update_output, update_error, history_id))
            
            conn.commit()
            conn.close()
            
            # 检查是否需要触发告警
            if status in ["completed", "failed"]:
                AlertHandler.check_alerts(history_id, status, error)
            
            logger.info(f"更新执行历史记录成功: ID {history_id}")
            return True
        except Exception as e:
            logger.error(f"更新执行历史记录失败: {str(e)}")
            return False
    
    @staticmethod
    def update_progress(history_id, output=None, error=None):
        """更新执行进度（不改变状态）"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前记录
            cursor.execute("SELECT * FROM execution_history WHERE id = ?", (history_id,))
            history = cursor.fetchone()
            
            if not history:
                logger.error(f"更新执行进度失败: 记录ID {history_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_output = output if output is not None else history['output']
            update_error = error if error is not None else history['error']
            
            cursor.execute('''
            UPDATE execution_history
            SET output = ?, error = ?
            WHERE id = ?
            ''', (update_output, update_error, history_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新执行进度成功: ID {history_id}")
            return True
        except Exception as e:
            logger.error(f"更新执行进度失败: {str(e)}")
            return False
    
    @staticmethod
    def get(history_id):
        """获取执行历史记录详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM execution_history
            WHERE id = ?
            ''', (history_id,))
            
            history = cursor.fetchone()
            
            if history and history['params']:
                try:
                    history['params'] = json.loads(history['params'])
                except:
                    pass
            
            conn.close()
            return history
        except Exception as e:
            logger.error(f"获取执行历史记录失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all(limit=50, offset=0, filters=None):
        """获取执行历史记录列表"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            query = '''
            SELECT 
                h.*, 
                s.name as script_name,
                c.name as chain_name
            FROM execution_history h
            LEFT JOIN scripts s ON h.script_id = s.id
            LEFT JOIN script_chains c ON h.chain_id = c.id
            '''
            
            params = []
            
            # 添加过滤条件
            if filters:
                where_clauses = []
                
                if filters.get('status'):
                    where_clauses.append("h.status = ?")
                    params.append(filters['status'])
                
                if filters.get('script_id'):
                    where_clauses.append("h.script_id = ?")
                    params.append(filters['script_id'])
                
                if filters.get('chain_id'):
                    where_clauses.append("h.chain_id = ?")
                    params.append(filters['chain_id'])
                
                if filters.get('start_date'):
                    where_clauses.append("h.start_time >= ?")
                    params.append(filters['start_date'])
                
                if filters.get('end_date'):
                    where_clauses.append("h.start_time <= ?")
                    params.append(filters['end_date'])
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            query += " ORDER BY h.start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            histories = cursor.fetchall()
            
            # 解析参数JSON
            for history in histories:
                if history['params']:
                    try:
                        history['params'] = json.loads(history['params'])
                    except:
                        pass
            
            conn.close()
            return histories
        except Exception as e:
            logger.error(f"获取执行历史记录列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_statistics(period='day', start_date=None, end_date=None, script_id=None, chain_id=None):
        """获取执行统计数据"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            # 根据周期确定分组方式
            if period == 'hour':
                time_format = '%Y-%m-%d %H'
                group_by = "strftime('%Y-%m-%d %H', start_time)"
            elif period == 'day':
                time_format = '%Y-%m-%d'
                group_by = "strftime('%Y-%m-%d', start_time)"
            elif period == 'week':
                time_format = '%Y-%W'  # 年-周数
                group_by = "strftime('%Y-%W', start_time)"
            elif period == 'month':
                time_format = '%Y-%m'
                group_by = "strftime('%Y-%m', start_time)"
            else:
                time_format = '%Y-%m-%d'
                group_by = "strftime('%Y-%m-%d', start_time)"
            
            # 构建查询
            query = f'''
            SELECT 
                {group_by} as time_period,
                COUNT(*) as total_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                AVG(execution_time) as avg_execution_time
            FROM execution_history
            '''
            
            params = []
            where_clauses = []
            
            # 添加过滤条件
            if start_date:
                where_clauses.append("start_time >= ?")
                params.append(start_date)
            
            if end_date:
                where_clauses.append("start_time <= ?")
                params.append(end_date)
            
            if script_id:
                where_clauses.append("script_id = ?")
                params.append(script_id)
            
            if chain_id:
                where_clauses.append("chain_id = ?")
                params.append(chain_id)
            
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += f" GROUP BY {group_by} ORDER BY time_period ASC"
            
            cursor.execute(query, params)
            stats = cursor.fetchall()
            
            conn.close()
            return stats
        except Exception as e:
            logger.error(f"获取执行统计数据失败: {str(e)}")
            return []


class AlertConfig:
    """告警配置模型类"""
    
    @staticmethod
    def add(name, description, alert_type, condition_type, condition_value, notification_type, notification_config):
        """添加告警配置"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            notification_config_json = json.dumps(notification_config) if isinstance(notification_config, dict) else notification_config
            
            cursor.execute('''
            INSERT INTO alert_configs
            (name, description, alert_type, condition_type, condition_value, notification_type, notification_config, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, alert_type, condition_type, condition_value, notification_type, notification_config_json, now, now))
            
            config_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加告警配置成功: {name}")
            return config_id
        except Exception as e:
            logger.error(f"添加告警配置失败: {str(e)}")
            return None
    
    @staticmethod
    def update(config_id, name=None, description=None, alert_type=None, condition_type=None, 
               condition_value=None, notification_type=None, notification_config=None, is_active=None):
        """更新告警配置"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前配置
            cursor.execute("SELECT * FROM alert_configs WHERE id = ?", (config_id,))
            config = cursor.fetchone()
            
            if not config:
                logger.error(f"更新告警配置失败: 配置ID {config_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_name = name if name is not None else config['name']
            update_desc = description if description is not None else config['description']
            update_alert_type = alert_type if alert_type is not None else config['alert_type']
            update_condition_type = condition_type if condition_type is not None else config['condition_type']
            update_condition_value = condition_value if condition_value is not None else config['condition_value']
            update_notification_type = notification_type if notification_type is not None else config['notification_type']
            
            if notification_config is not None:
                if isinstance(notification_config, dict):
                    update_notification_config = json.dumps(notification_config)
                else:
                    update_notification_config = notification_config
            else:
                update_notification_config = config['notification_config']
            
            update_is_active = is_active if is_active is not None else config['is_active']
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE alert_configs
            SET name = ?, description = ?, alert_type = ?, condition_type = ?, 
                condition_value = ?, notification_type = ?, notification_config = ?,
                is_active = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_alert_type, update_condition_type, 
                  update_condition_value, update_notification_type, update_notification_config,
                  update_is_active, now, config_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新告警配置成功: ID {config_id}")
            return True
        except Exception as e:
            logger.error(f"更新告警配置失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(config_id):
        """删除告警配置"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM alert_configs WHERE id = ?", (config_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除告警配置成功: ID {config_id}")
            return True
        except Exception as e:
            logger.error(f"删除告警配置失败: {str(e)}")
            return False
    
    @staticmethod
    def get(config_id):
        """获取告警配置详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM alert_configs
            WHERE id = ?
            ''', (config_id,))
            
            config = cursor.fetchone()
            
            if config and config['notification_config']:
                try:
                    config['notification_config'] = json.loads(config['notification_config'])
                except:
                    pass
            
            conn.close()
            return config
        except Exception as e:
            logger.error(f"获取告警配置失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all(is_active=None):
        """获取所有告警配置"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            query = "SELECT * FROM alert_configs"
            params = []
            
            if is_active is not None:
                query += " WHERE is_active = ?"
                params.append(is_active)
            
            query += " ORDER BY updated_at DESC"
            
            cursor.execute(query, params)
            configs = cursor.fetchall()
            
            # 解析通知配置JSON
            for config in configs:
                if config['notification_config']:
                    try:
                        config['notification_config'] = json.loads(config['notification_config'])
                    except:
                        pass
            
            conn.close()
            return configs
        except Exception as e:
            logger.error(f"获取告警配置列表失败: {str(e)}")
            return []


class AlertHistory:
    """告警历史模型类"""
    
    @staticmethod
    def add(alert_config_id, execution_id, status, message=None):
        """添加告警历史记录"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            INSERT INTO alert_history
            (alert_config_id, execution_id, status, message, sent_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (alert_config_id, execution_id, status, message, now))
            
            history_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加告警历史记录成功: 配置ID {alert_config_id}, 执行ID {execution_id}")
            return history_id
        except Exception as e:
            logger.error(f"添加告警历史记录失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all(limit=50, offset=0, alert_config_id=None):
        """获取告警历史记录列表"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            query = '''
            SELECT 
                ah.*, 
                ac.name as alert_name,
                eh.script_id,
                eh.chain_id,
                s.name as script_name,
                c.name as chain_name
            FROM alert_history ah
            JOIN alert_configs ac ON ah.alert_config_id = ac.id
            JOIN execution_history eh ON ah.execution_id = eh.id
            LEFT JOIN scripts s ON eh.script_id = s.id
            LEFT JOIN script_chains c ON eh.chain_id = c.id
            '''
            
            params = []
            
            if alert_config_id:
                query += " WHERE ah.alert_config_id = ?"
                params.append(alert_config_id)
            
            query += " ORDER BY ah.sent_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            histories = cursor.fetchall()
            
            conn.close()
            return histories
        except Exception as e:
            logger.error(f"获取告警历史记录列表失败: {str(e)}")
            return []
