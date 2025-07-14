import json
import inspect
from typing import List, Dict, Any, Optional
import importlib
import yaml
import os
import time # Added for time.time()

class Executor:
    """
    执行器负责运行计划中定义的任务。
    它调用必要的工具并收集结果。
    """

    def __init__(self, model_client=None, tool_modules: List[str] = [
        'intellicli.tools.file_system', 
        'intellicli.tools.shell', 
        'intellicli.tools.python_analyzer', 
        'intellicli.tools.system_operations',
        'intellicli.tools.code_analyzer',
        'intellicli.tools.git_operations', 
        'intellicli.tools.document_manager',
        'intellicli.tools.image_processor',
        'intellicli.tools.web_search',
        'intellicli.tools.content_integrator'
    ], config_path: str = "config.yaml"):
        """
        初始化执行器并动态加载可用工具。

        Args:
            model_client: 模型客户端实例，用于内容整合工具
            tool_modules (List[str]): 定义工具函数的模块列表。
            config_path (str): 配置文件路径
        """
        self.model_client = model_client
        self.config_path = config_path
        self.tools = {}  # 内置工具
        self.tool_info = {}  # 存储工具的详细信息
        self.mcp_manager = None  # MCP 工具管理器
        
        # 加载内置工具
        self._load_tools(tool_modules)
        
        # 加载 MCP 工具
        self._load_mcp_tools()
        
        # 如果提供了模型客户端，设置给内容整合工具
        if model_client:
            self._setup_content_integrator(model_client)

    def _is_builtin_or_imported(self, obj, module) -> bool:
        """判断对象是否为内置类型或从其他模块导入的对象"""
        # 检查是否为内置类型
        if hasattr(obj, '__module__'):
            obj_module = obj.__module__
            # 内置类型通常模块名为 'builtins' 或 None
            if obj_module in ('builtins', None):
                return True
            # 检查是否为标准库类型（如 datetime, collections等）
            if obj_module in ('datetime', 'collections', 'json', 'os', 'sys', 're', 'pathlib', 'typing'):
                return True
            # 检查是否不属于当前模块
            if module.__name__ != obj_module:
                return True
        return False

    def _load_tools(self, tool_modules: List[str]) -> None:
        """
        从指定模块动态导入工具函数，并提取其参数签名信息。
        """
        for module_name in tool_modules:
            try:
                module = importlib.import_module(module_name)
                # 查找模块中所有可调用且非私有的函数
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        # 过滤掉内置类型和非本模块定义的对象
                        if self._is_builtin_or_imported(attr, module):
                            continue
                            
                        # 存储函数本身
                        self.tools[attr_name] = attr
                        
                        # 提取函数签名信息
                        try:
                            sig = inspect.signature(attr)
                            parameters = []
                            
                            for param_name, param in sig.parameters.items():
                                param_info = {
                                    "name": param_name,
                                    "required": param.default == inspect.Parameter.empty,
                                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
                                }
                                parameters.append(param_info)
                            
                            self.tool_info[attr_name] = {
                                "name": attr_name,
                                "description": attr.__doc__ or "无描述",
                                "parameters": parameters
                            }
                        except Exception as e:
                            # 静默处理内置类型的签名提取失败，避免警告噪音
                            # 如果无法提取签名，至少保存基本信息
                            self.tool_info[attr_name] = {
                                "name": attr_name,
                                "description": attr.__doc__ or "无描述",
                                "parameters": []
                            }
            except ImportError as e:
                print(f"警告: 无法导入模块 {module_name}。{e}")

    def _setup_content_integrator(self, model_client):
        """设置内容整合工具的模型客户端"""
        try:
            from ..tools.content_integrator import set_model_client
            set_model_client(model_client)
        except ImportError as e:
            print(f"警告: 无法导入内容整合工具: {e}")
    
    def _load_mcp_tools(self):
        """加载 MCP 工具"""
        try:
            # 检查配置文件是否存在
            if not os.path.exists(self.config_path):
                print(f"配置文件 {self.config_path} 不存在，跳过 MCP 工具加载")
                return
            
            # 读取配置
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查是否有 MCP 配置
            mcp_config = config.get('mcp_servers', {})
            servers = mcp_config.get('servers', [])
            
            if not servers:
                print("💡 未配置 MCP 服务器，使用 'intellicli mcp-config' 来配置")
                return
            
            # 导入 MCP 相关模块
            try:
                from ..mcp.mcp_client import MCPServerConfig
                from ..mcp.mcp_tool_manager import MCPToolManager
            except ImportError as e:
                print(f"警告: 无法导入 MCP 模块: {e}")
                return
            
            # 创建服务器配置
            server_configs = []
            skipped_servers = []
            
            for server_config in servers:
                if not server_config.get('enabled', True):
                    skipped_servers.append(server_config.get('name', '未知'))
                    continue
                
                try:
                    config_obj = MCPServerConfig(
                        name=server_config['name'],
                        command=server_config['command'],
                        args=server_config.get('args', []),
                        env=server_config.get('env', {}),
                        description=server_config.get('description', ''),
                        auto_restart=server_config.get('auto_restart', True),
                        enabled=server_config.get('enabled', True)
                    )
                    server_configs.append(config_obj)
                except Exception as e:
                    print(f"⚠️ 跳过无效的服务器配置 '{server_config.get('name', '未知')}': {e}")
            
            if skipped_servers:
                print(f"ℹ️ 跳过了 {len(skipped_servers)} 个已禁用的 MCP 服务器")
            
            if not server_configs:
                print("📝 没有有效的 MCP 服务器配置")
                return
            
            # 创建 MCP 工具管理器
            self.mcp_manager = MCPToolManager(server_configs)
            
            # 连接到所有服务器
            print(f"🔗 正在连接到 {len(server_configs)} 个 MCP 服务器...")
            connection_results = self.mcp_manager.connect_all_servers()
            
            successful_connections = [name for name, success in connection_results.items() if success]
            failed_connections = [name for name, success in connection_results.items() if not success]
            
            if successful_connections:
                # 统计可用工具数量
                total_tools = sum(
                    len(self.mcp_manager.get_tools_by_server(server_name)) 
                    for server_name in successful_connections
                )
                print(f"✅ 成功连接到 {len(successful_connections)} 个 MCP 服务器，加载了 {total_tools} 个工具")
                print(f"   服务器: {', '.join(successful_connections)}")
                
                # 启动健康检查
                self.mcp_manager.start_health_check()
                
            if failed_connections:
                print(f"❌ {len(failed_connections)} 个 MCP 服务器连接失败:")
                for server_name in failed_connections:
                    server_status = self.mcp_manager.server_status.get(server_name, {})
                    error_msg = server_status.get('error', '未知错误')
                    print(f"   • {server_name}: {error_msg}")
                
                print(f"💡 提示: 确保已安装相应的 MCP 服务器包")
                print(f"   例如: npm install -g @modelcontextprotocol/server-filesystem")
                
        except Exception as e:
            print(f"❌ 加载 MCP 工具时出错: {e}")
            print(f"💡 可以使用 'intellicli mcp-status' 查看详细状态")

    def get_tool_info(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的详细信息，包括参数签名。
        
        Returns:
            List[Dict[str, Any]]: 包含工具名称、描述和参数信息的列表
        """
        all_tools = list(self.tool_info.values())
        
        # 添加 MCP 工具信息
        if self.mcp_manager:
            mcp_tools = self.mcp_manager.get_all_tools()
            all_tools.extend(mcp_tools)
        
        return all_tools

    def _process_argument(self, arg_value: Any, last_output: str) -> Any:
        """
        递归处理参数值，替换占位符。
        """
        if isinstance(arg_value, str):
            if "<PREVIOUS_STEP_OUTPUT>" in arg_value:
                # 如果占位符是整个字符串，直接替换
                if arg_value == "<PREVIOUS_STEP_OUTPUT>":
                    return last_output
                else:
                    # 如果占位符是字符串的一部分，进行替换
                    return arg_value.replace("<PREVIOUS_STEP_OUTPUT>", str(last_output))
            return arg_value
        elif isinstance(arg_value, list):
            # 处理列表参数
            processed_list = []
            for item in arg_value:
                if isinstance(item, str) and "<PREVIOUS_STEP_OUTPUT>" in item:
                    if item == "<PREVIOUS_STEP_OUTPUT>":
                        # 如果前一个输出是换行分隔的字符串，将其分割成列表
                        if isinstance(last_output, str) and '\n' in last_output:
                            processed_list.extend([p.strip() for p in last_output.split('\n') if p.strip()])
                        else:
                            processed_list.append(str(last_output))
                    else:
                        processed_list.append(item.replace("<PREVIOUS_STEP_OUTPUT>", str(last_output)))
                else:
                    processed_list.append(self._process_argument(item, last_output))
            return processed_list
        elif isinstance(arg_value, dict):
            return {k: self._process_argument(v, last_output) for k, v in arg_value.items()}
        else:
            return arg_value

    def execute_plan(self, plan: List[Dict[str, Any]], initial_output: str = "") -> List[Dict[str, Any]]:
        """
        逐步执行计划。

        Args:
            plan (List[Dict[str, Any]]): 要执行的任务列表。
            initial_output (str): 初始输出，用于续接执行时作为第一个<PREVIOUS_STEP_OUTPUT>的值

        Returns:
            List[Dict[str, Any]]: 包含每个已执行任务的详细结果的列表。
                                  每个结果字典包含 'step', 'tool', 'arguments', 'status', 'output' 和 'error'。
        """
        # 导入 UI 模块
        from ..ui.display import ui
        
        detailed_results = []
        total_steps = len(plan)
        last_output = initial_output or "" # 使用初始输出作为起始值
        
        # 记录总执行开始时间
        total_start_time = time.time()
        
        # 显示执行开始
        ui.print_execution_header()

        for i, task in enumerate(plan):
            step_num = i + 1
            tool_name = task.get("tool")
            arguments = task.get("arguments", {})
            
            # 使用增强的步骤执行显示
            ui.print_step_execution_enhanced(step_num, total_steps, tool_name, 
                                           model=getattr(self, 'model_name', None))
            
            # 替换占位符
            try:
                processed_arguments = {k: self._process_argument(v, last_output) for k, v in arguments.items()}
            except Exception as e:
                error_message = f"处理参数占位符时出错: {e}"
                step_result = {
                    "step": task.get('step', step_num),
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "failed",
                    "output": "",
                    "error": error_message
                }
                detailed_results.append(step_result)
                
                # 使用增强的完成显示
                ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                error_message, is_error=True)
                continue
            
            step_result = {
                "step": task.get('step', step_num),
                "tool": tool_name,
                "arguments": processed_arguments,
                "status": "failed", # 默认失败
                "output": "",
                "error": ""
            }

            if not tool_name:
                error_message = "工具名称为空"
                step_result['error'] = error_message
                detailed_results.append(step_result)
                
                # 使用增强的完成显示
                ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                error_message, is_error=True)
                continue

            # 检查是否是内置工具
            if tool_name in self.tools:
                try:
                    tool_function = self.tools[tool_name]
                    
                    # 检查工具函数是否存在
                    if not callable(tool_function):
                        error_message = f"工具 {tool_name} 不可调用"
                        step_result['error'] = error_message
                        detailed_results.append(step_result)
                        
                        # 使用增强的完成显示
                        ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                        error_message, is_error=True)
                        continue
                    
                    # 验证参数名称
                    if tool_name in self.tool_info:
                        expected_params = [p["name"] for p in self.tool_info[tool_name]["parameters"]]
                        provided_params = list(processed_arguments.keys())
                        
                        # 检查是否有无效的参数
                        invalid_params = [p for p in provided_params if p not in expected_params]
                        if invalid_params:
                            error_message = f"工具 {tool_name} 收到无效参数: {invalid_params}。期望参数: {expected_params}"
                            step_result['error'] = error_message
                            detailed_results.append(step_result)
                            
                            # 使用增强的完成显示
                            ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                            error_message, is_error=True)
                            continue
                    
                    # 对于长时间运行的任务显示警告
                    if tool_name == 'run_shell_command' and processed_arguments.get('command'):
                        command = processed_arguments['command']
                        if any(keyword in command.lower() for keyword in ['install', 'build', 'compile', 'download']):
                            ui.print_long_running_task_warning(f"Shell命令: {command[:50]}...")
                    
                    # 调用工具函数
                    output = tool_function(**processed_arguments)
                    
                    # 检查输出是否为错误信息
                    if isinstance(output, str) and ("出错" in output or "错误" in output or "Error" in output):
                        error_message = output
                        step_result['error'] = error_message
                        detailed_results.append(step_result)
                        
                        # 使用增强的完成显示
                        ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                        error_message, is_error=True)
                        continue
                    
                    # 成功执行
                    step_result['status'] = 'completed'
                    step_result['output'] = output
                    last_output = str(output) # 更新上一个输出，确保转换为字符串
                    
                    # 使用增强的完成显示
                    display_output = str(output)
                    ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                    display_output, is_error=False)
                    
                except TypeError as e:
                    error_message = f"工具 {tool_name} 参数错误: {e}"
                    step_result['error'] = error_message
                    
                    # 使用增强的完成显示
                    ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                    error_message, is_error=True)
                except Exception as e:
                    error_message = f"执行工具 {tool_name} 时出错: {e}"
                    step_result['error'] = error_message
                    
                    # 使用增强的完成显示
                    ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                    error_message, is_error=True)
            
            # 检查是否是 MCP 工具
            elif self.mcp_manager:
                is_mcp_tool = self.mcp_manager.is_mcp_tool(tool_name)
                if is_mcp_tool:
                    try:
                        # 调用 MCP 工具
                        output = self.mcp_manager.call_tool(tool_name, processed_arguments)
                        
                        step_result['status'] = 'completed'
                        step_result['output'] = output
                        last_output = str(output) # 更新上一个输出，确保转换为字符串
                        
                        # 使用增强的完成显示
                        display_output = str(output)
                        ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                        display_output, is_error=False)
                        
                    except Exception as e:
                        error_message = f"执行 MCP 工具 {tool_name} 时出错: {e}"
                        step_result['error'] = error_message
                        
                        # 使用增强的完成显示
                        ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                        error_message, is_error=True)
                else:
                    # 不是 MCP 工具，继续到 else 分支
                    pass
            
            else:
                # 工具不存在
                available_builtin_tools = list(self.tools.keys())
                available_mcp_tools = []
                if self.mcp_manager:
                    available_mcp_tools = list(self.mcp_manager.all_tools.keys())
                
                all_available_tools = available_builtin_tools + available_mcp_tools
                error_message = f"未找到工具 '{tool_name}'。可用工具: {all_available_tools[:10]}{'...' if len(all_available_tools) > 10 else ''}"
                step_result['error'] = error_message
                
                # 使用增强的完成显示
                ui.print_step_completion_enhanced(step_num, total_steps, tool_name, 
                                                error_message, is_error=True)
            
            detailed_results.append(step_result)

        # 计算总执行时间
        total_execution_time = time.time() - total_start_time
        
        # 统计执行结果
        completed_steps = [r for r in detailed_results if r['status'] == 'completed']
        failed_steps = [r for r in detailed_results if r['status'] == 'failed']
        
        # 使用增强的统计信息显示
        ui.print_execution_stats(
            total_time=total_execution_time,
            steps_executed=len(detailed_results),
            success_count=len(completed_steps),
            failure_count=len(failed_steps)
        )
        
        return detailed_results
    
    def get_mcp_status(self) -> Optional[Dict[str, Any]]:
        """获取 MCP 状态信息"""
        if not self.mcp_manager:
            return None
        
        return {
            "statistics": self.mcp_manager.get_statistics(),
            "server_status": self.mcp_manager.get_server_status(),
            "available_servers": self.mcp_manager.get_available_servers()
        }
    
    def refresh_mcp_tools(self):
        """刷新 MCP 工具"""
        if self.mcp_manager:
            self.mcp_manager.refresh_tools()
            print("MCP 工具已刷新")
        else:
            print("MCP 管理器未初始化")
    
    def __del__(self):
        """析构函数，确保 MCP 连接正确关闭"""
        if hasattr(self, 'mcp_manager') and self.mcp_manager:
            try:
                self.mcp_manager.stop_health_check()
                self.mcp_manager.disconnect_all_servers()
            except Exception as e:
                print(f"关闭 MCP 连接时出错: {e}")