# -*- coding: utf-8 -*-
"""
实时执行器
支持实时更新执行状态和进度
"""
import os
import sys
import json
import time
import threading
import subprocess
from models import ExecutionHistory
from config import logger

class RealtimeExecutor:
    """实时执行器，支持实时更新执行状态"""
    
    def __init__(self, history_id, script_path=None, chain_nodes=None, params=None):
        """
        初始化实时执行器
        
        Args:
            history_id: 执行历史ID
            script_path: 脚本路径（单个脚本执行时）
            chain_nodes: 链节点列表（链执行时）
            params: 执行参数
        """
        self.history_id = history_id
        self.script_path = script_path
        self.chain_nodes = chain_nodes
        self.params = params or {}
        self.process = None
        self.output_buffer = []
        self.error_buffer = []
        self.stopped = False
    
    def execute(self):
        """开始执行脚本或脚本链"""
        try:
            thread = threading.Thread(target=self._execute_task)
            thread.daemon = True
            thread.start()
            return True
        except Exception as e:
            logger.error(f"启动执行线程失败: {str(e)}")
            ExecutionHistory.update(self.history_id, "failed", None, f"启动执行失败: {str(e)}")
            return False
    
    def _execute_task(self):
        """执行任务的线程函数"""
        try:
            if self.script_path:
                self._execute_script()
            elif self.chain_nodes:
                self._execute_chain()
            else:
                ExecutionHistory.update(self.history_id, "failed", None, "未指定执行目标")
        except Exception as e:
            logger.error(f"执行任务失败: {str(e)}")
            ExecutionHistory.update(self.history_id, "failed", None, f"执行任务失败: {str(e)}")
    
    def _execute_script(self):
        """执行单个脚本"""
        try:
            if not os.path.exists(self.script_path):
                ExecutionHistory.update(self.history_id, "failed", None, f"脚本不存在: {self.script_path}")
                return
            
            # 获取脚本文件扩展名
            _, ext = os.path.splitext(self.script_path)
            ext = ext.lstrip('.').lower()
            
            # 准备参数
            params_file = self._write_params_file(self.params)
            if not params_file:
                ExecutionHistory.update(self.history_id, "failed", None, "创建参数文件失败")
                return
            
            # 根据脚本类型执行不同的命令
            if ext == 'py':
                cmd = [sys.executable, self.script_path, params_file]
            elif ext in ['sh', 'bash']:
                cmd = ['bash', self.script_path, params_file]
            elif ext == 'bat':
                cmd = [self.script_path, params_file]
            elif ext == 'ps1':
                cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', self.script_path, params_file]
            elif ext == 'js':
                cmd = ['node', self.script_path, params_file]
            else:
                ExecutionHistory.update(self.history_id, "failed", None, f"不支持的脚本类型: {ext}")
                return
            
            # 开始执行命令
            self._start_process(cmd)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
        except Exception as e:
            ExecutionHistory.update(self.history_id, "failed", None, f"执行脚本失败: {str(e)}")
    
    def _execute_chain(self):
        """执行脚本链"""
        try:
            outputs = {}
            prev_output = None
            
            for i, node in enumerate(self.chain_nodes):
                if self.stopped:
                    break
                    
                script_id = node['script_id']
                script_path = node['file_path']
                node_name = node.get('script_name', f'节点{i+1}')
                
                # 更新执行进度
                progress_msg = f"正在执行节点 {i+1}/{len(self.chain_nodes)}: {node_name}"
                current_output = "\n".join(self.output_buffer)
                current_error = "\n".join(self.error_buffer)
                ExecutionHistory.update_progress(
                    self.history_id, 
                    f"{current_output}\n{progress_msg}", 
                    current_error
                )
                
                # 准备节点参数
                node_params = self.params.copy() if self.params else {}
                if prev_output is not None:
                    node_params['__prev_output'] = prev_output
                
                # 准备参数文件
                params_file = self._write_params_file(node_params)
                if not params_file:
                    self.error_buffer.append(f"节点 {i+1} 创建参数文件失败")
                    ExecutionHistory.update(
                        self.history_id, 
                        "failed", 
                        "\n".join(self.output_buffer), 
                        "\n".join(self.error_buffer)
                    )
                    return
                
                # 获取脚本文件扩展名
                _, ext = os.path.splitext(script_path)
                ext = ext.lstrip('.').lower()
                
                # 构建命令
                if ext == 'py':
                    cmd = [sys.executable, script_path, params_file]
                elif ext in ['sh', 'bash']:
                    cmd = ['bash', script_path, params_file]
                elif ext == 'bat':
                    cmd = [script_path, params_file]
                elif ext == 'ps1':
                    cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path, params_file]
                elif ext == 'js':
                    cmd = ['node', script_path, params_file]
                else:
                    self.error_buffer.append(f"节点 {i+1} 不支持的脚本类型: {ext}")
                    ExecutionHistory.update(
                        self.history_id, 
                        "failed", 
                        "\n".join(self.output_buffer), 
                        "\n".join(self.error_buffer)
                    )
                    return
                
                # 执行节点命令
                self.output_buffer.append(f"\n--- 执行节点 {i+1}/{len(self.chain_nodes)}: {node_name} ---\n")
                
                # 重置节点输出和错误缓冲区
                node_output = []
                node_error = []
                
                # 开始进程
                success = self._start_process(cmd, node_output, node_error)
                
                # 清理参数文件
                try:
                    os.unlink(params_file)
                except:
                    pass
                
                # 保存节点执行结果
                node_result = {
                    'output': "\n".join(node_output),
                    'error': "\n".join(node_error),
                    'success': success
                }
                outputs[script_id] = node_result
                
                # 如果节点执行失败，终止链执行
                if not success:
                    self.error_buffer.append(f"节点 {i+1} 执行失败: {node_result['error']}")
                    ExecutionHistory.update(
                        self.history_id, 
                        "failed", 
                        json.dumps(outputs), 
                        f"节点 {i+1} 执行失败: {node_result['error']}"
                    )
                    return
                
                # 保存输出用于下一个节点
                prev_output = node_result['output']
            
            # 链执行完成
            if not self.stopped:
                ExecutionHistory.update(
                    self.history_id, 
                    "completed", 
                    json.dumps(outputs), 
                    None
                )
            
        except Exception as e:
            ExecutionHistory.update(
                self.history_id, 
                "failed", 
                json.dumps(outputs) if 'outputs' in locals() else None,
                f"执行脚本链失败: {str(e)}"
            )
    
    def _write_params_file(self, params):
        """将参数写入临时文件"""
        import tempfile
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as temp:
                json.dump(params, temp, ensure_ascii=False, indent=2)
                return temp.name
        except Exception as e:
            logger.error(f"写入参数文件失败: {str(e)}")
            return None
    
    def _start_process(self, cmd, output_buffer=None, error_buffer=None):
        """启动进程执行命令"""
        if output_buffer is None:
            output_buffer = self.output_buffer
        if error_buffer is None:
            error_buffer = self.error_buffer
        
        try:
            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 创建读取输出的线程
            def read_output():
                for line in self.process.stdout:
                    if line:
                        output_buffer.append(line.rstrip())
                        # 每隔一段时间更新进度
                        if len(output_buffer) % 10 == 0 and not self.stopped:
                            ExecutionHistory.update_progress(
                                self.history_id, 
                                "\n".join(output_buffer), 
                                "\n".join(error_buffer)
                            )
            
            # 创建读取错误输出的线程
            def read_error():
                for line in self.process.stderr:
                    if line:
                        error_buffer.append(line.rstrip())
                        # 每当有错误时立即更新
                        if not self.stopped:
                            ExecutionHistory.update_progress(
                                self.history_id, 
                                "\n".join(output_buffer), 
                                "\n".join(error_buffer)
                            )
            
            # 启动输出读取线程
            stdout_thread = threading.Thread(target=read_output)
            stderr_thread = threading.Thread(target=read_error)
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程结束
            self.process.wait()
            stdout_thread.join()
            stderr_thread.join()
            
            # 检查进程返回码
            success = self.process.returncode == 0
            self.process = None
            
            return success
            
        except Exception as e:
            error_buffer.append(f"执行进程时出错: {str(e)}")
            if not self.stopped:
                ExecutionHistory.update_progress(
                    self.history_id, 
                    "\n".join(output_buffer), 
                    "\n".join(error_buffer)
                )
            
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                except:
                    pass
                self.process = None
            
            return False
    
    def stop(self):
        """停止执行"""
        self.stopped = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(0.2)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass
            
            ExecutionHistory.update(
                self.history_id, 
                "failed", 
                "\n".join(self.output_buffer), 
                "\n".join(self.error_buffer) + "\n执行被手动终止"
            )
            return True
        return False
