# -*- coding: utf-8 -*-
"""
定时任务模型模块
定义定时任务相关数据库模型和操作
"""
import datetime
import json
import croniter
from .base import DBManager
from config import logger

class ScheduledTask:
    """定时任务模型类"""
    
    @staticmethod
    def add(name, description, schedule_type, cron_expression, script_id=None, chain_id=None, params=None):
        """添加定时任务"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            params_json = json.dumps(params) if params else None
            
            # 计算下次执行时间
            next_run = ScheduledTask.calculate_next_run(cron_expression)
            
            cursor.execute('''
            INSERT INTO scheduled_tasks
            (name, description, script_id, chain_id, schedule_type, cron_expression, params, is_active, next_run, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, script_id, chain_id, schedule_type, cron_expression, params_json, 1, next_run, now, now))
            
            task_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"添加定时任务成功: {name}")
            return task_id
        except Exception as e:
            logger.error(f"添加定时任务失败: {str(e)}")
            return None
    
    @staticmethod
    def update(task_id, name=None, description=None, schedule_type=None, cron_expression=None, 
              script_id=None, chain_id=None, params=None, is_active=None):
        """更新定时任务"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前任务信息
            cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()
            
            if not task:
                logger.error(f"更新定时任务失败: 任务ID {task_id} 不存在")
                conn.close()
                return False
            
            # 准备更新数据
            update_name = name if name is not None else task['name']
            update_desc = description if description is not None else task['description']
            update_type = schedule_type if schedule_type is not None else task['schedule_type']
            update_cron = cron_expression if cron_expression is not None else task['cron_expression']
            update_script_id = script_id if script_id is not None else task['script_id']
            update_chain_id = chain_id if chain_id is not None else task['chain_id']
            
            if params is not None:
                params_json = json.dumps(params)
            else:
                params_json = task['params']
            
            update_active = is_active if is_active is not None else task['is_active']
            
            # 如果cron表达式发生变化，重新计算下次执行时间
            if cron_expression and cron_expression != task['cron_expression']:
                next_run = ScheduledTask.calculate_next_run(cron_expression)
            else:
                next_run = task['next_run']
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            UPDATE scheduled_tasks
            SET name = ?, description = ?, script_id = ?, chain_id = ?, 
                schedule_type = ?, cron_expression = ?, params = ?,
                is_active = ?, next_run = ?, updated_at = ?
            WHERE id = ?
            ''', (update_name, update_desc, update_script_id, update_chain_id, 
                 update_type, update_cron, params_json, update_active, next_run, now, task_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新定时任务成功: ID {task_id}")
            return True
        except Exception as e:
            logger.error(f"更新定时任务失败: {str(e)}")
            return False
    
    @staticmethod
    def delete(task_id):
        """删除定时任务"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"删除定时任务成功: ID {task_id}")
            return True
        except Exception as e:
            logger.error(f"删除定时任务失败: {str(e)}")
            return False
    
    @staticmethod
    def get(task_id):
        """获取定时任务详情"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT st.*, s.name as script_name, c.name as chain_name
            FROM scheduled_tasks st
            LEFT JOIN scripts s ON st.script_id = s.id
            LEFT JOIN script_chains c ON st.chain_id = c.id
            WHERE st.id = ?
            ''', (task_id,))
            
            task = cursor.fetchone()
            
            if task and task['params']:
                try:
                    task['params'] = json.loads(task['params'])
                except:
                    pass
            
            conn.close()
            return task
        except Exception as e:
            logger.error(f"获取定时任务详情失败: {str(e)}")
            return None
    
    @staticmethod
    def get_all(is_active=None):
        """获取所有定时任务"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            query = '''
            SELECT st.*, s.name as script_name, c.name as chain_name
            FROM scheduled_tasks st
            LEFT JOIN scripts s ON st.script_id = s.id
            LEFT JOIN script_chains c ON st.chain_id = c.id
            '''
            
            params = []
            
            if is_active is not None:
                query += " WHERE st.is_active = ?"
                params.append(is_active)
            
            query += " ORDER BY st.next_run ASC"
            
            cursor.execute(query, params)
            tasks = cursor.fetchall()
            
            # 解析参数JSON
            for task in tasks:
                if task['params']:
                    try:
                        task['params'] = json.loads(task['params'])
                    except:
                        pass
            
            conn.close()
            return tasks
        except Exception as e:
            logger.error(f"获取定时任务列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_due_tasks():
        """获取到期需要执行的任务"""
        try:
            conn = DBManager.get_connection()
            conn.row_factory = DBManager.dict_factory
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
            SELECT * FROM scheduled_tasks
            WHERE is_active = 1 AND next_run <= ?
            ORDER BY next_run ASC
            ''', (now,))
            
            tasks = cursor.fetchall()
            
            # 解析参数JSON
            for task in tasks:
                if task['params']:
                    try:
                        task['params'] = json.loads(task['params'])
                    except:
                        pass
            
            conn.close()
            return tasks
        except Exception as e:
            logger.error(f"获取到期任务失败: {str(e)}")
            return []
    
    @staticmethod
    def update_after_execution(task_id, execution_time=None):
        """执行后更新任务的执行时间和下次执行时间"""
        try:
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # 获取当前任务信息
            cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()
            
            if not task:
                logger.error(f"更新任务执行信息失败: 任务ID {task_id} 不存在")
                conn.close()
                return False
            
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 计算下次执行时间
            next_run = ScheduledTask.calculate_next_run(task['cron_expression'])
            
            cursor.execute('''
            UPDATE scheduled_tasks
            SET last_run = ?, next_run = ?
            WHERE id = ?
            ''', (now, next_run, task_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"更新任务执行信息成功: ID {task_id}, 下次执行时间 {next_run}")
            return True
        except Exception as e:
            logger.error(f"更新任务执行信息失败: {str(e)}")
            return False
    
    @staticmethod
    def calculate_next_run(cron_expression):
        """计算下一次执行时间"""
        try:
            # 基于当前时间计算下一次执行时间
            now = datetime.datetime.now()
            cron = croniter.croniter(cron_expression, now)
            next_dt = cron.get_next(datetime.datetime)
            return next_dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.error(f"计算下次执行时间失败: {str(e)}")
            # 默认设置为1小时后
            next_dt = datetime.datetime.now() + datetime.timedelta(hours=1)
            return next_dt.strftime('%Y-%m-%d %H:%M:%S')
