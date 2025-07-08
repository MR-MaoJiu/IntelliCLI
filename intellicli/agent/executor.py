import json
import inspect
from typing import List, Dict, Any
import importlib

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
    ]):
        """
        初始化执行器并动态加载可用工具。

        Args:
            model_client: 模型客户端实例，用于内容整合工具
            tool_modules (List[str]): 定义工具函数的模块列表。
        """
        self.model_client = model_client
        self.tools = {}
        self.tool_info = {}  # 存储工具的详细信息
        self._load_tools(tool_modules)
        
        # 如果提供了模型客户端，设置给内容整合工具
        if model_client:
            self._setup_content_integrator(model_client)

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
                            print(f"警告: 无法提取工具 {attr_name} 的签名信息: {e}")
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

    def get_tool_info(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的详细信息，包括参数签名。
        
        Returns:
            List[Dict[str, Any]]: 包含工具名称、描述和参数信息的列表
        """
        return list(self.tool_info.values())

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

    def execute_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        逐步执行计划。

        Args:
            plan (List[Dict[str, Any]]): 要执行的任务列表。

        Returns:
            List[Dict[str, Any]]: 包含每个已执行任务的详细结果的列表。
                                  每个结果字典包含 'step', 'tool', 'arguments', 'status', 'output' 和 'error'。
        """
        detailed_results = []
        total_steps = len(plan)
        last_output = "" # 用于存储上一个成功步骤的输出

        for i, task in enumerate(plan):
            step_num = i + 1
            print(f"\n[执行步骤 {step_num}/{total_steps}]: {task.get('tool')}...")
            
            tool_name = task.get("tool")
            arguments = task.get("arguments", {})
            
            # 替换占位符
            try:
                processed_arguments = {k: self._process_argument(v, last_output) for k, v in arguments.items()}
            except Exception as e:
                error_message = f"处理参数占位符时出错: {e}"
                print(f"  \\_ 错误: {error_message}")
                step_result = {
                    "step": task.get('step', step_num),
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "failed",
                    "output": "",
                    "error": error_message
                }
                detailed_results.append(step_result)
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
                print(f"  \\_ 错误: {error_message}")
                step_result['error'] = error_message
                detailed_results.append(step_result)
                continue

            if tool_name in self.tools:
                try:
                    tool_function = self.tools[tool_name]
                    
                    # 检查工具函数是否存在
                    if not callable(tool_function):
                        error_message = f"工具 {tool_name} 不可调用"
                        print(f"  \\_ 错误: {error_message}")
                        step_result['error'] = error_message
                        detailed_results.append(step_result)
                        continue
                    
                    # 验证参数名称
                    if tool_name in self.tool_info:
                        expected_params = [p["name"] for p in self.tool_info[tool_name]["parameters"]]
                        provided_params = list(processed_arguments.keys())
                        
                        # 检查是否有无效的参数
                        invalid_params = [p for p in provided_params if p not in expected_params]
                        if invalid_params:
                            error_message = f"工具 {tool_name} 收到无效参数: {invalid_params}。期望参数: {expected_params}"
                            print(f"  \\_ 错误: {error_message}")
                            step_result['error'] = error_message
                            detailed_results.append(step_result)
                            continue
                    
                    # 调用工具函数
                    output = tool_function(**processed_arguments)
                    
                    # 检查输出是否为错误信息
                    if isinstance(output, str) and ("出错" in output or "错误" in output or "Error" in output):
                        error_message = output
                        print(f"  \\_ 错误: {error_message}")
                        step_result['error'] = error_message
                        detailed_results.append(step_result)
                        continue
                    
                    # 格式化输出显示
                    if isinstance(output, dict):
                        display_output = json.dumps(output, indent=2, ensure_ascii=False)
                    else:
                        display_output = str(output)
                    
                    # 限制显示长度
                    if len(display_output) > 200:
                        print(f"  \\_ 结果: {display_output[:200]}...")
                    else:
                        print(f"  \\_ 结果: {display_output}")
                    
                    step_result['status'] = 'completed'
                    step_result['output'] = output
                    last_output = str(output) # 更新上一个输出，确保转换为字符串
                    
                except TypeError as e:
                    error_message = f"工具 {tool_name} 参数错误: {e}"
                    print(f"  \\_ 错误: {error_message}")
                    step_result['error'] = error_message
                except Exception as e:
                    error_message = f"执行工具 {tool_name} 时出错: {e}"
                    print(f"  \\_ 错误: {error_message}")
                    step_result['error'] = error_message
            else:
                available_tools = list(self.tools.keys())
                error_message = f"未找到工具 '{tool_name}'。可用工具: {available_tools}"
                print(f"  \\_ 错误: {error_message}")
                step_result['error'] = error_message
            
            detailed_results.append(step_result)

        print("\n执行完成。")
        
        # 统计执行结果
        completed_steps = [r for r in detailed_results if r['status'] == 'completed']
        failed_steps = [r for r in detailed_results if r['status'] == 'failed']
        
        print(f"总步骤: {len(detailed_results)}, 成功: {len(completed_steps)}, 失败: {len(failed_steps)}")
        
        return detailed_results