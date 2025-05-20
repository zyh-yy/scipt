# -*- coding: utf-8 -*-
"""
脚本执行器
用于执行不同类型的脚本，并处理输入输出
"""
import os
import sys
import json
import time
import signal
import subprocess
import tempfile
from pathlib import Path
import threading
from config import SCRIPT_TIMEOUT, ALLOWED_EXTENSIONS, USE_DOCKER, logger
from .docker_executor import DockerExecutor

class ScriptRunner:
    """脚本执行器类，负责执行各种类型的脚本"""
    
    @staticmethod
    def run_script(script_path, params=None, prev_output=None, use_docker=None):
        """
        执行脚本
        
        Args:
            script_path: 脚本文件路径
            params: 脚本参数字典
            prev_output: 上一个脚本的输出（链式执行时使用）
            use_docker: 是否使用Docker容器执行，None表示使用配置默认值
            
        Returns:
            tuple: (success, output, error)
        """
        if not os.path.exists(script_path):
            return False, None, f"脚本不存在: {script_path}"
        
        # 获取脚本文件扩展名
        _, ext = os.path.splitext(script_path)
        ext = ext.lstrip('.').lower()
        
        if ext not in ALLOWED_EXTENSIONS:
            return False, None, f"不支持的脚本类型: {ext}"
        
        # 准备参数和上一个脚本的输出
        prepared_params = ScriptRunner._prepare_params(params, prev_output)
        
        # 确定是否使用Docker执行
        use_docker_execution = USE_DOCKER if use_docker is None else use_docker
        
        # 如果启用Docker执行
        if use_docker_execution:
            logger.info(f"使用Docker容器执行脚本: {script_path}")
            return DockerExecutor.run_script_in_docker(script_path, prepared_params, prev_output)
        
        # 直接在主机上执行脚本
        # 根据脚本类型执行不同的命令
        if ext == 'py':
            return ScriptRunner._run_python_script(script_path, prepared_params)
        elif ext in ['sh', 'bash']:
            return ScriptRunner._run_shell_script(script_path, prepared_params)
        elif ext == 'bat':
            return ScriptRunner._run_batch_script(script_path, prepared_params)
        elif ext == 'ps1':
            return ScriptRunner._run_powershell_script(script_path, prepared_params)
        elif ext == 'js':
            return ScriptRunner._run_js_script(script_path, prepared_params)
        else:
            return False, None, f"未实现的脚本类型: {ext}"
    
    @staticmethod
    def _prepare_params(params, prev_output):
        """
        准备脚本参数
        
        Args:
            params: 用户提供的参数字典
            prev_output: 上一个脚本的输出
            
        Returns:
            dict: 准备好的参数字典
        """
        prepared_params = params.copy() if params else {}
        
        # 添加上一个脚本的输出作为特殊参数
        if prev_output is not None:
            prepared_params['__prev_output'] = prev_output
        
        return prepared_params
    
    @staticmethod
    def _write_params_file(params):
        """
        将参数写入临时文件
        
        Args:
            params: 参数字典
            
        Returns:
            str: 临时文件路径
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as temp:
                json.dump(params, temp, ensure_ascii=False, indent=2)
                return temp.name
        except Exception as e:
            logger.error(f"写入参数文件失败: {str(e)}")
            return None
    
    @staticmethod
    def _run_process_with_timeout(cmd, env=None, shell=False):
        """
        带超时的子进程执行
        
        Args:
            cmd: 要执行的命令
            env: 环境变量
            shell: 是否在shell中执行
            
        Returns:
            tuple: (success, output, error)
        """
        process = None
        timer = None
        output_buffer = []
        error_buffer = []
        terminated = False
        
        try:
            # 准备环境变量
            if env is None:
                env = os.environ.copy()
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=shell,
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 设置超时定时器
            def kill_process():
                nonlocal terminated
                terminated = True
                logger.warning(f"脚本执行超时，强制终止: {cmd}")
                if process and process.poll() is None:
                    if os.name == 'nt':  # Windows
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                    else:  # Linux/Unix
                        try:
                            process.kill()
                        except:
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            
            timer = threading.Timer(SCRIPT_TIMEOUT, kill_process)
            timer.daemon = True
            timer.start()
            
            # 实时读取输出
            for line in process.stdout:
                output_buffer.append(line)
            
            # 读取错误输出
            for line in process.stderr:
                error_buffer.append(line)
            
            # 等待进程结束
            process.wait()
            
            # 取消超时定时器
            if timer:
                timer.cancel()
            
            output = ''.join(output_buffer).strip()
            error = ''.join(error_buffer).strip()
            
            if terminated:
                return False, output, f"脚本执行超时，已强制终止 (超时设置: {SCRIPT_TIMEOUT}秒)"
            
            success = process.returncode == 0
            return success, output, error if not success else None
            
        except Exception as e:
            if timer:
                timer.cancel()
            
            if process and process.poll() is None:
                try:
                    process.kill()
                except:
                    pass
            
            logger.error(f"执行进程时出错: {str(e)}")
            return False, None, f"执行进程时出错: {str(e)}"
    
    @staticmethod
    def _run_python_script(script_path, params):
        """执行Python脚本"""
        logger.info(f"执行Python脚本: {script_path}")
        
        # 写入参数到临时文件
        params_file = ScriptRunner._write_params_file(params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        try:
            # 构建命令
            cmd = [sys.executable, script_path, params_file]
            
            # 执行命令
            success, output, error = ScriptRunner._run_process_with_timeout(cmd)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
            
            return success, output, error
        except Exception as e:
            logger.error(f"执行Python脚本失败: {str(e)}")
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
            return False, None, f"执行Python脚本失败: {str(e)}"
    
    @staticmethod
    def _run_shell_script(script_path, params):
        """执行Shell脚本"""
        logger.info(f"执行Shell脚本: {script_path}")
        
        # 写入参数到临时文件
        params_file = ScriptRunner._write_params_file(params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        try:
            # 确保脚本有执行权限（仅在Unix系统上需要）
            if os.name != 'nt':  # 非Windows系统
                try:
                    os.chmod(script_path, 0o755)
                except:
                    pass
            
            # 构建命令
            cmd = ['bash', script_path, params_file]
            
            # 执行命令
            success, output, error = ScriptRunner._run_process_with_timeout(cmd)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
            
            return success, output, error
        except Exception as e:
            logger.error(f"执行Shell脚本失败: {str(e)}")
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
            return False, None, f"执行Shell脚本失败: {str(e)}"
    
    @staticmethod
    def _run_batch_script(script_path, params):
        """执行Batch脚本"""
        logger.info(f"执行Batch脚本: {script_path}")
        
        # 写入参数到临时文件
        params_file = ScriptRunner._write_params_file(params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        try:
            # 构建命令
            cmd = [script_path, params_file]
            
            # 执行命令
            success, output, error = ScriptRunner._run_process_with_timeout(cmd, shell=True)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
            
            return success, output, error
        except Exception as e:
            logger.error(f"执行Batch脚本失败: {str(e)}")
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
            return False, None, f"执行Batch脚本失败: {str(e)}"
    
    @staticmethod
    def _run_powershell_script(script_path, params):
        """执行PowerShell脚本"""
        logger.info(f"执行PowerShell脚本: {script_path}")
        
        # 写入参数到临时文件
        params_file = ScriptRunner._write_params_file(params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        try:
            # 构建命令
            cmd = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path, params_file]
            
            # 执行命令
            success, output, error = ScriptRunner._run_process_with_timeout(cmd)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
            
            return success, output, error
        except Exception as e:
            logger.error(f"执行PowerShell脚本失败: {str(e)}")
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
            return False, None, f"执行PowerShell脚本失败: {str(e)}"
    
    @staticmethod
    def _run_js_script(script_path, params):
        """执行JavaScript脚本"""
        logger.info(f"执行JavaScript脚本: {script_path}")
        
        # 写入参数到临时文件
        params_file = ScriptRunner._write_params_file(params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        try:
            # 构建命令
            cmd = ['node', script_path, params_file]
            
            # 执行命令
            success, output, error = ScriptRunner._run_process_with_timeout(cmd)
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
            
            return success, output, error
        except Exception as e:
            logger.error(f"执行JavaScript脚本失败: {str(e)}")
            
            # 清理临时文件
            try:
                os.unlink(params_file)
            except:
                pass
                
            return False, None, f"执行JavaScript脚本失败: {str(e)}"
    
    @staticmethod
    def run_script_chain(chain_nodes, params=None, use_docker=None):
        """
        执行脚本链
        
        Args:
            chain_nodes: 链节点列表，包含脚本路径
            params: 初始脚本参数
            use_docker: 是否使用Docker容器执行，None表示使用配置默认值
            
        Returns:
            tuple: (success, outputs, error)
                outputs是一个字典，键是脚本ID，值是输出
        """
        # 确定是否使用Docker执行
        use_docker_execution = USE_DOCKER if use_docker is None else use_docker
        
        # 如果启用Docker执行，使用Docker执行脚本链
        if use_docker_execution:
            logger.info(f"使用Docker容器执行脚本链: 共{len(chain_nodes)}个节点")
            return DockerExecutor.run_script_chain_in_docker(chain_nodes, params)
        
        # 直接在主机上执行脚本链
        outputs = {}
        prev_output = None
        
        for i, node in enumerate(chain_nodes):
            script_id = node['script_id']
            script_path = node['file_path']
            
            logger.info(f"执行脚本链节点 {i+1}/{len(chain_nodes)}: ID={script_id}, 路径={script_path}")
            
            # 第一个脚本使用初始参数，后续脚本使用前一个脚本的输出作为输入
            if i == 0:
                node_params = params
            else:
                # 后续节点会同时接收用户传入的参数和前一个脚本的输出
                node_params = params.copy() if params else {}
            
            # 执行脚本
            success, output, error = ScriptRunner.run_script(
                script_path, 
                node_params, 
                prev_output,
                use_docker=False  # 确保在链执行中的单个脚本不再使用Docker（因为整个链已经决定了执行方式）
            )
            
            # 保存结果
            outputs[script_id] = {
                'output': output,
                'error': error,
                'success': success
            }
            
            # 如果一个脚本执行失败，整个链就失败
            if not success:
                logger.error(f"脚本链执行失败: 节点 {i+1}/{len(chain_nodes)}, ID={script_id}, 错误={error}")
                return False, outputs, f"节点 {i+1} 失败: {error}"
            
            # 保存输出用于下一个脚本
            prev_output = output
        
        return True, outputs, None
