# -*- coding: utf-8 -*-
"""
Docker容器执行器
用于在Docker容器中执行脚本，并回收执行结果
"""
import os
import json
import tempfile
import subprocess
import threading
import time
from pathlib import Path
from config import logger, UPLOAD_FOLDER

class DockerExecutor:
    """Docker容器执行器类，负责在Docker容器中执行脚本"""
    
    @staticmethod
    def check_docker_installed():
        """检查Docker是否已安装并可用"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                    capture_output=True, 
                                    text=True, 
                                    check=False)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"检查Docker安装失败: {str(e)}")
            return False
    
    @staticmethod
    def run_script_in_docker(script_path, params=None, prev_output=None, 
                             image="python:3.9-slim", timeout=300):
        """
        在Docker容器中执行脚本
        
        Args:
            script_path: 脚本文件路径
            params: 脚本参数字典
            prev_output: 上一个脚本的输出（链式执行时使用）
            image: Docker镜像名称
            timeout: 执行超时时间（秒）
            
        Returns:
            tuple: (success, output, error)
        """
        if not os.path.exists(script_path):
            return False, None, f"脚本不存在: {script_path}"
        
        # 检查Docker是否可用
        if not DockerExecutor.check_docker_installed():
            return False, None, "Docker未安装或不可用"
        
        # 获取脚本文件扩展名
        _, ext = os.path.splitext(script_path)
        ext = ext.lstrip('.').lower()
        
        # 准备标准化参数结构
        standard_params = {
            "user_params": {},
            "system_params": {
                "__execution_time": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "file_params": {}
        }
        
        # 填充用户参数
        if params and isinstance(params, dict):
            # 如果已经是标准化结构，保持原样
            if all(key in params for key in ["user_params", "system_params", "file_params"]):
                standard_params = params.copy()
            # 否则，假设它是用户参数
            else:
                standard_params["user_params"] = params.copy()
        
        # 添加上一个脚本的输出
        if prev_output is not None:
            standard_params["system_params"]["__prev_output"] = prev_output
            
        # 记录参数传递情况
        logger.info(f"传递给Docker容器的参数: {json.dumps(standard_params, ensure_ascii=False)[:500]}...")
        
        # 准备参数文件
        params_file = DockerExecutor._write_params_file(standard_params)
        if not params_file:
            return False, None, "无法创建参数文件"
        
        # 如果是Python脚本，准备requirements文件
        requirements_file = None
        if ext == 'py':
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            requirements_path = os.path.join(project_root, 'requirements.txt')
            
            # 复制requirements.txt到临时目录
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r', encoding='utf-8') as src:
                    requirements_content = src.read()
                    
                requirements_file = os.path.join(os.path.dirname(params_file), 'requirements.txt')
                with open(requirements_file, 'w', encoding='utf-8') as dest:
                    dest.write(requirements_content)
        
        # 创建临时输出文件
        output_file = tempfile.mktemp(suffix='.out')
        error_file = tempfile.mktemp(suffix='.err')
        
        try:
            # 准备挂载卷
            script_dir = os.path.dirname(script_path)
            script_name = os.path.basename(script_path)
            params_name = os.path.basename(params_file)
            
            # 根据脚本类型选择合适的Docker镜像和命令
            docker_image = DockerExecutor._get_docker_image(ext, image)
            docker_cmd = DockerExecutor._get_docker_command(ext, script_name, params_name)
            
            # 构建Docker运行命令
            cmd = [
                'docker', 'run', '--rm',
                '-v', f"{script_dir}:/app",
                '-v', f"{os.path.dirname(params_file)}:/params",
                '-w', '/app',
                '--network=host',  # 允许网络访问，根据需要可以移除
                docker_image
            ]
            cmd.extend(docker_cmd)
            
            # 记录详细的执行过程
            logger.info(f"准备在Docker中执行脚本: {script_path}")
            logger.info(f"使用Docker镜像: {docker_image}")
            logger.info(f"执行Docker命令: {' '.join(cmd)}")
            
            with open(output_file, 'w', encoding='utf-8') as out_f, \
                 open(error_file, 'w', encoding='utf-8') as err_f:
                
                process = subprocess.Popen(
                    cmd,
                    stdout=out_f,
                    stderr=err_f,
                    text=True,
                    encoding='utf-8'
                )
                
                # 设置超时控制
                timer = threading.Timer(timeout, DockerExecutor._kill_process, args=[process])
                timer.daemon = True
                timer.start()
                
                # 等待进程完成
                process.wait()
                
                # 取消定时器
                timer.cancel()
            
            # 读取输出和错误
            with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
                output = f.read()
            
            with open(error_file, 'r', encoding='utf-8', errors='replace') as f:
                error = f.read()
            
            # 判断是否成功并记录执行结果
            success = process.returncode == 0
            
            # 记录容器日志和执行状态
            logger.info(f"Docker执行完成，返回码: {process.returncode}")
            if not success:
                logger.error(f"Docker执行失败，错误信息: {error}")
            else:
                logger.info(f"Docker执行成功，输出长度: {len(output) if output else 0}")
            
            return success, output, error if not success else None
            
        except Exception as e:
            logger.error(f"在Docker中执行脚本失败: {str(e)}")
            return False, None, f"在Docker中执行脚本失败: {str(e)}"
        finally:
            # 清理临时文件
            for file in [params_file, output_file, error_file, requirements_file]:
                try:
                    if file and os.path.exists(file):
                        os.unlink(file)
                except:
                    pass
    
    @staticmethod
    def run_script_chain_in_docker(chain_nodes, params=None, image=None):
        """
        在Docker容器中执行脚本链
        
        Args:
            chain_nodes: 链节点列表，包含脚本路径
            params: 初始脚本参数
            image: Docker镜像名称（可选，如果不指定则根据脚本类型选择）
            
        Returns:
            tuple: (success, outputs, error)
                outputs是一个字典，键是脚本ID，值是输出
        """
        outputs = {}
        prev_output = None
        
        # 准备标准化参数结构
        standard_params = {
            "user_params": {},
            "system_params": {
                "__execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "__chain_execution": True
            },
            "file_params": {}
        }
        
        # 填充用户参数
        if params and isinstance(params, dict):
            # 如果已经是标准化结构，保持原样
            if all(key in params for key in ["user_params", "system_params", "file_params"]):
                standard_params = params.copy()
            # 否则，假设它是用户参数
            else:
                standard_params["user_params"] = params.copy()
        
        for i, node in enumerate(chain_nodes):
            script_id = node['script_id']
            script_path = node['file_path']
            
            logger.info(f"在Docker中执行脚本链节点 {i+1}/{len(chain_nodes)}: ID={script_id}, 路径={script_path}")
            
            # 第一个脚本使用初始参数，后续脚本使用前一个脚本的输出作为输入
            if i == 0:
                node_params = standard_params
            else:
                # 后续节点会同时接收用户传入的参数和前一个脚本的输出
                node_params = standard_params.copy()
                # 添加前一个脚本的输出
                if prev_output is not None:
                    node_params["system_params"]["__prev_output"] = prev_output
            
            # 获取脚本类型
            _, ext = os.path.splitext(script_path)
            ext = ext.lstrip('.').lower()
            
            # 如果未指定镜像，根据脚本类型选择
            node_image = image or DockerExecutor._get_docker_image(ext)
            
            # 执行脚本
            success, output, error = DockerExecutor.run_script_in_docker(
                script_path, 
                node_params, 
                prev_output,
                node_image
            )
            
            # 保存结果
            outputs[script_id] = {
                'output': output,
                'error': error,
                'success': success
            }
            
            # 如果一个脚本执行失败，整个链就失败
            if not success:
                logger.error(f"脚本链在Docker中执行失败: 节点 {i+1}/{len(chain_nodes)}, ID={script_id}, 错误={error}")
                return False, outputs, f"节点 {i+1} 失败: {error}"
            
            # 保存输出用于下一个脚本
            prev_output = output
        
        return True, outputs, None
    
    @staticmethod
    def _write_params_file(params):
        """将参数写入临时文件"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', encoding='utf-8') as temp:
                json.dump(params, temp, ensure_ascii=False, indent=2)
                return temp.name
        except Exception as e:
            logger.error(f"写入参数文件失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_docker_image(script_ext, default_image=None):
        """根据脚本类型获取合适的Docker镜像"""
        if default_image:
            return default_image
            
        image_map = {
            'py': 'python:3.9-slim',
            'js': 'node:16-alpine',
            'sh': 'ubuntu:20.04',
            'bash': 'ubuntu:20.04',
            'ps1': 'mcr.microsoft.com/powershell:latest',
            'bat': 'mcr.microsoft.com/windows/servercore:ltsc2019'  # 注意：Windows容器需要Windows宿主机
        }
        
        return image_map.get(script_ext, 'python:3.9-slim')
    
    @staticmethod
    def _extract_python_imports(script_path):
        """从Python脚本中提取导入的包名"""
        if not os.path.exists(script_path):
            return []
        
        try:
            imports = set()
            with open(script_path, 'r', encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    # 匹配import语句
                    if line.startswith('import '):
                        # 处理 "import package"
                        package = line[7:].strip().split(' ')[0].split('.')[0]
                        if package and package != 'os' and package != 'sys' and package != 'json':
                            imports.add(package)
                    # 匹配from...import语句
                    elif line.startswith('from '):
                        # 处理 "from package import xxx"
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            package = parts[1].split('.')[0]
                            if package and package != 'os' and package != 'sys' and package != 'json':
                                imports.add(package)
            
            return list(imports)
        except Exception as e:
            logger.error(f"提取Python导入包失败: {str(e)}")
            return []
    
    @staticmethod
    def _create_requirements_file(base_requirements_path, additional_packages=None):
        """创建包含所有依赖的临时requirements文件"""
        try:
            # 读取基础requirements文件
            requirements = []
            if os.path.exists(base_requirements_path):
                with open(base_requirements_path, 'r', encoding='utf-8') as f:
                    requirements = [line.strip() for line in f if line.strip()]
            
            # 添加额外的包
            if additional_packages:
                for package in additional_packages:
                    if not any(req.startswith(f"{package}==") or req == package for req in requirements):
                        requirements.append(package)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp:
                for req in requirements:
                    temp.write(f"{req}\n")
                return temp.name
        except Exception as e:
            logger.error(f"创建requirements文件失败: {str(e)}")
            return None
    
    @staticmethod
    def _get_docker_command(script_ext, script_name, params_name):
        """根据脚本类型获取Docker容器中的执行命令"""
        if script_ext == 'py':
            # 对于Python脚本，直接使用Python解释器执行脚本
            # 避免使用source命令（在某些shell中不支持）
            # 使用项目根目录的requirements.txt
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            requirements_path = os.path.join(project_root, 'requirements.txt')
            
            return [
                'sh', '-c',
                f"pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && "
                f"pip config set global.trusted-host mirrors.aliyun.com && "
                f"pip install --no-cache-dir --user -r /params/requirements.txt && "
                f"pip install --no-cache-dir --user psutil && "  # 确保安装psutil
                f"python /app/{script_name} /params/{params_name}"
            ]
        
        cmd_map = {
            'py': ['python', f"/app/{script_name}", f"/params/{params_name}"],
            'js': ['node', f"/app/{script_name}", f"/params/{params_name}"],
            'sh': ['bash', f"/app/{script_name}", f"/params/{params_name}"],
            'bash': ['bash', f"/app/{script_name}", f"/params/{params_name}"],
            'ps1': ['pwsh', '-File', f"/app/{script_name}", f"/params/{params_name}"],
            'bat': ['cmd.exe', '/C', f"C:\\app\\{script_name}", f"C:\\params\\{params_name}"]  # Windows容器
        }
        
        return cmd_map.get(script_ext, ['python', f"/app/{script_name}", f"/params/{params_name}"])
    
    @staticmethod
    def _kill_process(process):
        """终止进程（超时处理）"""
        if process and process.poll() is None:
            try:
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()
            except:
                pass
