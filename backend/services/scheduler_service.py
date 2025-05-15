# -*- coding: utf-8 -*-
"""
定时任务调度服务
负责定时执行脚本和脚本链
"""
import time
import threading
import datetime
import croniter
from models import ScheduledTask, ExecutionHistory
from utils.realtime_executor import RealtimeExecutor
from config import logger

class SchedulerService:
    """定时任务调度服务类"""
    
    def __init__(self):
        """初始化调度器"""
        self.running = False
        self.check_interval = 30  # 检查间隔（秒）
        self.thread = None
        self.executors = {}  # 存储正在执行的任务执行器 {history_id: executor}
    
    def start(self):
        """启动调度服务"""
        if self.running:
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._schedule_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("定时任务调度服务已启动")
        return True
    
    def stop(self):
        """停止调度服务"""
        if not self.running:
            return False
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=60)
            self.thread = None
        
        # 停止所有正在执行的任务
        for executor in list(self.executors.values()):
            executor.stop()
        
        logger.info("定时任务调度服务已停止")
        return True
    
    def _schedule_loop(self):
        """调度循环"""
        while self.running:
            try:
                self._check_and_execute_tasks()
            except Exception as e:
                logger.error(f"定时任务调度循环出错: {str(e)}")
            
            # 等待下一次检查
            for _ in range(self.check_interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _check_and_execute_tasks(self):
        """检查并执行到期的任务"""
        # 清理已完成的执行器
        self._clean_finished_executors()
        
        # 获取到期任务
        tasks = ScheduledTask.get_due_tasks()
        
        for task in tasks:
            try:
                # 检查任务类型并执行
                if task['script_id']:
                    # 单脚本任务
                    self._execute_script_task(task)
                elif task['chain_id']:
                    # 脚本链任务
                    self._execute_chain_task(task)
                
                # 更新任务的执行时间
                ScheduledTask.update_after_execution(task['id'])
                
            except Exception as e:
                logger.error(f"执行定时任务失败: 任务ID {task['id']}, 错误: {str(e)}")
    
    def _execute_script_task(self, task):
        """执行脚本任务"""
        from models import Script
        
        script_id = task['script_id']
        script = Script.get(script_id)
        
        if not script:
            logger.error(f"定时任务执行失败: 脚本不存在, 脚本ID {script_id}")
            return
        
        # 获取脚本路径和参数
        script_path = script['file_path']
        params = task['params'] if task['params'] else {}
        
        # 创建执行历史记录
        history_id = ExecutionHistory.add(
            script_id=script_id,
            status="running",
            params=params
        )
        
        if not history_id:
            logger.error(f"创建执行历史记录失败: 任务ID {task['id']}")
            return
        
        # 创建实时执行器并开始执行
        executor = RealtimeExecutor(history_id, script_path=script_path, params=params)
        success = executor.execute()
        
        if success:
            # 保存执行器以便后续管理
            self.executors[history_id] = executor
            logger.info(f"定时任务启动成功: 任务ID {task['id']}, 历史ID {history_id}")
        else:
            logger.error(f"定时任务启动失败: 任务ID {task['id']}, 历史ID {history_id}")
    
    def _execute_chain_task(self, task):
        """执行脚本链任务"""
        from models import ScriptChain, ChainNode
        
        chain_id = task['chain_id']
        chain = ScriptChain.get(chain_id)
        
        if not chain:
            logger.error(f"定时任务执行失败: 脚本链不存在, 脚本链ID {chain_id}")
            return
        
        # 获取链节点和参数
        nodes = chain.get('nodes', [])
        if not nodes:
            logger.error(f"定时任务执行失败: 脚本链中没有节点, 脚本链ID {chain_id}")
            return
        
        params = task['params'] if task['params'] else {}
        
        # 创建执行历史记录
        history_id = ExecutionHistory.add(
            chain_id=chain_id,
            status="running",
            params=params
        )
        
        if not history_id:
            logger.error(f"创建执行历史记录失败: 任务ID {task['id']}")
            return
        
        # 创建实时执行器并开始执行
        executor = RealtimeExecutor(history_id, chain_nodes=nodes, params=params)
        success = executor.execute()
        
        if success:
            # 保存执行器以便后续管理
            self.executors[history_id] = executor
            logger.info(f"定时任务启动成功: 任务ID {task['id']}, 历史ID {history_id}")
        else:
            logger.error(f"定时任务启动失败: 任务ID {task['id']}, 历史ID {history_id}")
    
    def _clean_finished_executors(self):
        """清理已完成的执行器"""
        to_remove = []
        
        for history_id, executor in self.executors.items():
            # 检查执行历史状态
            history = ExecutionHistory.get(history_id)
            if history and history['status'] in ['completed', 'failed']:
                to_remove.append(history_id)
        
        # 移除已完成的执行器
        for history_id in to_remove:
            self.executors.pop(history_id, None)
    
    def stop_execution(self, history_id):
        """停止指定的执行任务"""
        executor = self.executors.get(history_id)
        if executor:
            success = executor.stop()
            if success:
                self.executors.pop(history_id, None)
            return success
        return False

# 全局调度器实例
scheduler = SchedulerService()
