import typer
import yaml
import os
import inspect # 导入 inspect 模块

from typing import Optional, List, Dict, Any

from .agent.planner import Planner
from .agent.executor import Executor
from .agent.model_router import ModelRouter
from .agent.agent import Agent as IntelliAgent
from .config.model_config import ModelConfigManager
from .config.search_config import SearchConfigManager
from .models.ollama_client import OllamaClient
from .models.gemini_client import GeminiClient
from .models.deepseek_client import DeepSeekClient
from .models.openai_client import OpenAIClient
from .models.claude_client import ClaudeClient
from .ui.display import ui  # 导入现代化UI

app = typer.Typer()

def load_config():
    """从 config.yaml 加载配置，如果不存在则运行配置向导。"""
    config_manager = ModelConfigManager()
    
    # 检查是否有有效配置
    if not config_manager.has_valid_config():
        ui.print_warning("⚠️  未找到有效的模型配置")
        ui.print_info("🚀 将启动配置向导帮助您设置 IntelliCLI")
        
        # 运行配置向导
        success = config_manager.run_config_wizard()
        if not success:
            ui.print_error("❌ 配置失败，无法继续")
            raise typer.Exit(code=1)
        
        ui.print_success("✅ 配置完成！正在启动 IntelliCLI...")
        ui.print_info("")
    
    # 验证配置
    if not config_manager.validate_config():
        ui.print_error("❌ 配置文件验证失败")
        raise typer.Exit(code=1)
    
    # 加载配置
    with open("config.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_model_clients(config: dict) -> Dict[str, Any]:
    """根据配置初始化所有模型客户端。"""
    model_clients = {}
    model_providers = config['models']['providers']
    
    for model_info in model_providers:
        alias = model_info['alias']
        try:
            if model_info['provider'] == 'ollama':
                client = OllamaClient(
                    model_name=model_info['model_name'],
                    base_url=model_info.get('base_url', 'http://localhost:11434')
                )
            elif model_info['provider'] == 'gemini':
                client = GeminiClient(
                    model_name=model_info['model_name'],
                    api_key=model_info.get('api_key')
                )
            elif model_info['provider'] == 'openai':
                client = OpenAIClient(
                    model_name=model_info['model_name'],
                    api_key=model_info.get('api_key'),
                    base_url=model_info.get('base_url')
                )
            elif model_info['provider'] == 'deepseek':
                client = DeepSeekClient(
                    model_name=model_info['model_name'],
                    api_key=model_info.get('api_key'),
                    base_url=model_info.get('base_url', 'https://api.deepseek.com')
                )
            elif model_info['provider'] == 'claude':
                client = ClaudeClient(
                    model_name=model_info['model_name'],
                    api_key=model_info.get('api_key')
                )
            else:
                ui.print_warning(f"不支持的模型提供商: {model_info['provider']}")
                continue
            
            model_clients[alias] = client
            ui.print_info(f"✅ 已初始化模型: {alias} ({model_info['model_name']})")
        except Exception as e:
            ui.print_error(f"❌ 初始化模型 {alias} 失败: {e}")
    
    return model_clients

def get_model_client(config: dict):
    """根据配置初始化并返回主模型客户端。"""
    primary_model_alias = config['models']['primary']
    model_providers = config['models']['providers']
    
    model_info = next((p for p in model_providers if p['alias'] == primary_model_alias), None)
    
    if not model_info:
        raise ValueError(f"配置中未找到主模型 '{primary_model_alias}'。")

    if model_info['provider'] == 'ollama':
        return OllamaClient(
            model_name=model_info['model_name'],
            base_url=model_info.get('base_url')  # 如果存在，则传递 base_url
        )
    elif model_info['provider'] == 'gemini':
        return GeminiClient(
            model_name=model_info['model_name'],
            api_key=model_info.get('api_key')
        )
    elif model_info['provider'] == 'openai':
        return OpenAIClient(
            model_name=model_info['model_name'],
            api_key=model_info.get('api_key'),
            base_url=model_info.get('base_url')
        )
    elif model_info['provider'] == 'deepseek':
        return DeepSeekClient(
            model_name=model_info['model_name'],
            api_key=model_info.get('api_key'),
            base_url=model_info.get('base_url', 'https://api.deepseek.com')
        )
    elif model_info['provider'] == 'claude':
        return ClaudeClient(
            model_name=model_info['model_name'],
            api_key=model_info.get('api_key')
        )
    else:
        raise ValueError(f"不支持的模型提供商: {model_info['provider']}")

class Agent:
    """
    Agent 类协调 Planner 和 Executor，实现动态任务规划和自动纠错。
    """
    def __init__(self, model_router: ModelRouter, planner: Planner, executor: Executor):
        self.model_router = model_router
        self.planner = planner
        self.executor = executor
        self.context = [] # 用于存储执行历史和结果，作为 Planner 的输入
        self.max_context_length = 5 # 最多保留最近的 N 个上下文条目
        self.current_goal = None
        self.task_active = False
        self.session_memory = {  # 会话记忆
            "created_files": [],
            "visited_directories": [],
            "last_operations": [],
            "project_context": ""
        }
        # 任务执行历史（用于复盘功能）
        self.execution_history = []
        
        # 获取主模型客户端，用于规划阶段
        self.primary_model_client = self._get_primary_model_client()

    def _get_primary_model_client(self):
        """获取主模型客户端"""
        # 从配置中获取主模型
        primary_model = self.model_router.config.get('models', {}).get('primary')
        if primary_model:
            return self.model_router.get_model_client(primary_model)
        
        # 如果没有配置主模型，返回第一个可用模型
        available_models = list(self.model_router.model_clients.keys())
        if available_models:
            return self.model_router.get_model_client(available_models[0])
        
        return None

    def _update_session_memory(self, plan: List[Dict[str, Any]], results: List[Dict[str, Any]]):
        """更新会话记忆"""
        for i, (step, result) in enumerate(zip(plan, results)):
            if result['status'] == 'completed':
                tool_name = step.get('tool')
                args = step.get('arguments', {})
                
                # 记录文件操作
                if tool_name == 'write_file' and 'path' in args:
                    file_path = args['path']
                    if file_path not in self.session_memory["created_files"]:
                        self.session_memory["created_files"].append(file_path)
                
                # 记录目录访问
                elif tool_name in ['list_directory', 'start_http_server'] and 'path' in args:
                    dir_path = args.get('path') or args.get('directory')
                    if dir_path and dir_path not in self.session_memory["visited_directories"]:
                        self.session_memory["visited_directories"].append(dir_path)
                
                # 记录最近操作
                operation = f"{tool_name}: {args}"
                self.session_memory["last_operations"].append(operation)
                if len(self.session_memory["last_operations"]) > 10:
                    self.session_memory["last_operations"].pop(0)

    def _generate_context_prompt(self, goal: str) -> str:
        """生成包含丰富上下文信息的提示"""
        context_info = []
        
        # 添加会话记忆信息
        if self.session_memory["created_files"]:
            context_info.append(f"最近创建的文件: {', '.join(self.session_memory['created_files'][-3:])}")
        
        if self.session_memory["visited_directories"]:
            context_info.append(f"最近访问的目录: {', '.join(self.session_memory['visited_directories'][-3:])}")
        
        if self.session_memory["last_operations"]:
            context_info.append(f"最近的操作: {'; '.join(self.session_memory['last_operations'][-3:])}")
        
        # 构建基础提示
        base_prompt = f"当前目标: {goal}"
        
        if context_info:
            base_prompt += f"\n\n会话上下文:\n" + "\n".join(f"- {info}" for info in context_info)
        
        # 添加失败历史
        context_for_planner = self.context[-self.max_context_length:]
        if context_for_planner:
            base_prompt += f"\n\n历史执行记录: {context_for_planner}"
            base_prompt += "\n\n**重要提示：根据历史上下文中的失败信息，生成一个全新的、不同的计划。避免重复相同的失败步骤。**"
        
        # 添加智能建议
        base_prompt += f"""

**任务理解指南:**
- 如果目标涉及"运行"、"打开"HTML文件，使用 open_file 工具打开文件
- 如果需要启动Web服务器来运行HTML项目，使用 start_http_server 工具
- 如果目标涉及创建文件后立即使用，考虑文件的具体用途
- 充分利用会话上下文中的信息，理解任务的连续性

请根据当前目标、会话上下文和历史记录，生成一个详细的、可执行的步骤列表。

**您的响应必须仅是 JSON 数组。**"""
        
        return base_prompt

    def _run_task_iteration(self, goal: str, max_planning_attempts: int = 5) -> bool:
        """
        运行一个任务的单次规划和执行迭代。
        返回 True 如果任务完成，否则返回 False。
        """
        current_plan = []
        for p_attempt in range(max_planning_attempts):
            # 使用现代化UI显示规划尝试
            ui.print_planning_attempt(p_attempt + 1, max_planning_attempts)
            
            # 规划阶段：固定使用主模型进行整体思考规划
            ui.print_info(f"🧠 规划阶段: 使用主模型进行整体思考规划")
            
            # 确保规划器使用主模型
            if self.primary_model_client:
                self.planner.model_client = self.primary_model_client
            else:
                ui.print_error("无法获取主模型客户端")
                return False
            
            # 生成智能化的规划提示
            planning_prompt = self._generate_context_prompt(goal)

            # 获取规划器可用的工具列表，包含详细的参数信息
            available_tools = self.executor.get_tool_info()

            current_plan = self.planner.create_plan(planning_prompt, available_tools)
            
            if not current_plan:
                ui.print_error("规划器未能生成有效计划。重试规划...")
                continue
            
            # 检查是否生成了与之前相同的计划
            if self._is_duplicate_plan(current_plan):
                ui.print_warning("检测到重复计划，尝试生成新的计划...")
                continue
            
            # 使用现代化UI显示计划
            ui.print_plan(current_plan)

            if typer.confirm("您要执行此计划吗？"):
                # 使用现代化UI显示执行开始
                ui.print_execution_header()
                
                # 执行计划并使用新UI显示进度，传入目标用于智能模型选择
                execution_results = self._execute_plan_with_ui(current_plan, goal)
                
                # 更新会话记忆
                self._update_session_memory(current_plan, execution_results)
                
                # 更新上下文
                self.context.append({"plan": current_plan, "results": execution_results})

                failed_steps = [res for res in execution_results if res['status'] == 'failed']
                
                # 显示执行摘要
                total_steps = len(execution_results)
                success_steps = len([res for res in execution_results if res['status'] == 'completed'])
                ui.print_execution_summary(total_steps, success_steps, len(failed_steps))
                
                if not failed_steps:
                    # 记录成功完成的任务到历史中
                    self._record_task_to_history(goal, current_plan, execution_results, True)
                    return True # 任务成功完成
                else:
                    ui.print_info(f"尝试重新规划...")
                    # 将失败信息添加到上下文，以便规划器可以学习
                    self.context.append({"failed_steps": failed_steps, "attempt": p_attempt + 1})
                    continue # 继续下一次规划尝试
            else:
                ui.print_info("用户取消了计划执行。任务终止。")
                return False
        
        ui.print_error("代理在多次尝试后未能完成任务。")
        # 记录失败的任务到历史中
        if current_plan:
            final_results = self.context[-1].get('results', []) if self.context else []
            self._record_task_to_history(goal, current_plan, final_results, False)
        return False

    def _execute_plan_with_ui(self, plan: List[Dict[str, Any]], goal: str) -> List[Dict[str, Any]]:
        """使用现代UI执行计划，并为每个步骤选择最合适的专业模型"""
        results = []
        total_steps = len(plan)
        
        for i, task in enumerate(plan):
            step_num = i + 1
            tool_name = task.get("tool")
            arguments = task.get("arguments", {})
            
            # 显示步骤开始
            ui.print_step_execution(step_num, total_steps, tool_name, "running")
            
            # 为当前步骤选择最合适的专业模型
            selected_model = self._select_model_for_step(task, goal)
            ui.print_info(f"  🤖 执行模型: {selected_model}")
            
            # 处理占位符
            try:
                last_output = ""
                if results:
                    last_successful = [r for r in results if r['status'] == 'completed']
                    if last_successful:
                        last_output = str(last_successful[-1]['output'])
                
                processed_arguments = {k: self.executor._process_argument(v, last_output) for k, v in arguments.items()}
            except Exception as e:
                error_message = f"处理参数占位符时出错: {e}"
                ui.print_step_result(error_message, is_error=True)
                result = {
                    "step": task.get('step', step_num),
                    "tool": tool_name,
                    "arguments": arguments,
                    "status": "failed",
                    "output": "",
                    "error": error_message
                }
                results.append(result)
                ui.print_step_execution(step_num, total_steps, tool_name, "failed")
                continue
            
            # 执行工具，传入选定的模型客户端
            selected_model_client = self.model_router.get_model_client(selected_model)
            result = self._execute_single_step(task, processed_arguments, step_num, selected_model_client)
            
            # 显示执行结果
            if result['status'] == 'completed':
                ui.print_step_result(str(result['output']))
                ui.print_step_execution(step_num, total_steps, tool_name, "success")
            else:
                ui.print_step_result(result['error'], is_error=True)
                ui.print_step_execution(step_num, total_steps, tool_name, "failed")
            
            results.append(result)
        
        return results

    def _select_model_for_step(self, task: Dict[str, Any], goal: str) -> str:
        """为特定步骤选择最合适的专业模型"""
        tool_name = task.get("tool")
        arguments = task.get("arguments", {})
        
        # 构建步骤描述用于模型选择
        step_description = f"执行工具 {tool_name}"
        
        # 根据工具类型和参数增强描述
        if tool_name in ["integrate_content", "summarize_content", "extract_information"]:
            step_description += " - 内容处理和整合任务"
        elif tool_name in ["analyze_image", "describe_image", "identify_objects_in_image"]:
            step_description += " - 图像分析和视觉任务"
        elif tool_name in ["analyze_code_quality", "find_security_issues", "analyze_project_structure"]:
            step_description += " - 代码分析和编程任务"
        elif tool_name in ["web_search", "search_news", "search_academic"]:
            step_description += " - 网络搜索和信息检索任务"
        elif tool_name in ["generate_project_readme", "extract_api_documentation"]:
            step_description += " - 文档生成和技术写作任务"
        
        # 检查参数中是否包含图像路径
        task_context = {"file_paths": []}
        for key, value in arguments.items():
            if isinstance(value, str) and any(ext in value.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                task_context["file_paths"].append(value)
        
        # 使用模型路由器选择专业模型
        return self.model_router.route_task(step_description, task_context)

    def _execute_single_step(self, task: Dict[str, Any], processed_arguments: Dict[str, Any], step_num: int, model_client) -> Dict[str, Any]:
        """执行单个步骤，使用指定的模型客户端"""
        tool_name = task.get("tool")
        
        result = {
            "step": task.get('step', step_num),
            "tool": tool_name,
            "arguments": processed_arguments,
            "status": "failed",
            "output": "",
            "error": ""
        }
        
        if tool_name in self.executor.tools:
            try:
                tool_function = self.executor.tools[tool_name]
                
                # 验证参数
                if tool_name in self.executor.tool_info:
                    expected_params = [p["name"] for p in self.executor.tool_info[tool_name]["parameters"]]
                    provided_params = list(processed_arguments.keys())
                    invalid_params = [p for p in provided_params if p not in expected_params]
                    
                    if invalid_params:
                        error_message = f"工具 {tool_name} 收到无效参数: {invalid_params}。期望参数: {expected_params}"
                        result['error'] = error_message
                        return result
                
                # 对于需要模型客户端的工具，传入选定的模型客户端
                if self._tool_needs_model_client(tool_name):
                    # 临时设置模型客户端
                    self._set_tool_model_client(tool_name, model_client)
                
                # 调用工具
                output = tool_function(**processed_arguments)
                
                # 检查是否为错误输出
                if isinstance(output, str) and ("出错" in output or "错误" in output or "Error" in output):
                    result['error'] = output
                else:
                    result['status'] = 'completed'
                    result['output'] = output
                    
            except Exception as e:
                error_message = f"执行工具 {tool_name} 时出错: {e}"
                result['error'] = error_message
        else:
            error_message = f"未找到工具 '{tool_name}'"
            result['error'] = error_message
        
        return result

    def _tool_needs_model_client(self, tool_name: str) -> bool:
        """检查工具是否需要模型客户端"""
        model_dependent_tools = [
            "integrate_content", "summarize_content", "extract_information", 
            "transform_format", "analyze_image", "describe_image", 
            "identify_objects_in_image", "extract_text_from_image",
            "generate_project_readme", "extract_api_documentation"
        ]
        return tool_name in model_dependent_tools

    def _set_tool_model_client(self, tool_name: str, model_client):
        """为特定工具设置模型客户端"""
        if tool_name in ["integrate_content", "summarize_content", "extract_information", "transform_format"]:
            # 设置内容整合工具的模型客户端
            try:
                from .tools.content_integrator import set_model_client
                set_model_client(model_client)
            except ImportError:
                pass
        elif tool_name in ["analyze_image", "describe_image", "identify_objects_in_image", "extract_text_from_image"]:
            # 设置图像处理工具的模型客户端
            try:
                from .tools.image_processor import set_model_client
                set_model_client(model_client)
            except ImportError:
                pass

    def _is_duplicate_plan(self, new_plan: List[Dict[str, Any]]) -> bool:
        """检查新计划是否与之前的计划重复"""
        if not self.context:
            return False
        
        for context_item in self.context[-3:]:
            if 'plan' in context_item:
                old_plan = context_item['plan']
                if self._plans_are_similar(new_plan, old_plan):
                    return True
        return False

    def _plans_are_similar(self, plan1: List[Dict[str, Any]], plan2: List[Dict[str, Any]]) -> bool:
        """比较两个计划是否相似"""
        if len(plan1) != len(plan2):
            return False
        
        for i, (step1, step2) in enumerate(zip(plan1, plan2)):
            if step1.get('tool') != step2.get('tool'):
                return False
            if step1.get('arguments') != step2.get('arguments'):
                return False
        
        return True

    def _record_task_to_history(self, goal: str, plan: List[Dict[str, Any]], results: List[Dict[str, Any]], success: bool):
        """记录任务到执行历史中（用于复盘功能）"""
        from datetime import datetime
        
        # 计算成功率
        total_steps = len(results)
        successful_steps = len([r for r in results if r.get('status') == 'completed'])
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        # 构建历史记录条目
        history_entry = {
            'goal': goal,
            'success_rate': success_rate,
            'reviewed': False,  # 还未复盘
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'plan': plan,
            'results': results,
            'status': 'completed' if success else 'failed'
        }
        
        self.execution_history.append(history_entry)
        
        # 限制历史记录数量，保留最近的20条
        if len(self.execution_history) > 20:
            self.execution_history = self.execution_history[-20:]

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史（兼容复盘功能）"""
        return self.execution_history

    def clear_session_memory(self):
        """清空会话记忆"""
        self.session_memory = {
            "created_files": [],
            "visited_directories": [],
            "last_operations": [],
            "project_context": ""
        }
        self.context = []
        ui.print_success("会话记忆已清空")

    def show_model_info(self):
        """显示模型路由信息"""
        models_info = self.model_router.list_available_models()
        ui.print_section_header("可用模型信息", "🧠")
        
        for alias, info in models_info.items():
            capabilities = ", ".join(info["capabilities"])
            ui.print_info(f"• {alias}: {info['model_name']} ({info['provider']}) - {capabilities}")

    def _handle_review_command(self):
        """处理session模式下的review命令"""
        try:
            config = load_config()
            
            # 检查复盘功能是否启用
            review_config = config.get('task_review', {})
            if not review_config.get('enabled', False):
                ui.print_review_disabled()
                return
            
            # 检查是否有执行历史
            if not self.execution_history:
                ui.print_warning("没有可复盘的任务历史")
                return
            
            # 初始化模型客户端
            primary_client = get_model_client(config)
            
            # 使用当前Agent的历史记录进行复盘
            ui.print_info("🔍 开始复盘最近的任务")
            
            # 获取最近的任务
            last_execution = self.execution_history[-1]
            goal = last_execution['goal']
            plan = last_execution.get('plan', [])
            results = last_execution.get('results', [])
            
            ui.print_info(f"复盘目标: {goal}")
            
            # 创建任务复盘器进行分析
            from .agent.task_reviewer import TaskReviewer
            task_reviewer = TaskReviewer(primary_client)
            
            review_result = task_reviewer.review_task_execution(
                original_goal=goal,
                execution_plan=plan,
                execution_results=results
            )
            
            # 显示复盘结果
            self._display_review_results(review_result)
            
            # 标记为已复盘
            last_execution['reviewed'] = True
            
            ui.print_success("✅ 复盘完成")
                
        except Exception as e:
            ui.print_error(f"复盘过程中出错: {e}")

    def _handle_history_command(self):
        """处理session模式下的history命令"""
        try:
            # 直接使用当前Agent的执行历史
            ui.print_task_history(self.execution_history)
                
        except Exception as e:
            ui.print_error(f"获取历史记录时出错: {e}")

    def _display_review_results(self, review_result: Dict[str, Any]):
        """显示复盘结果"""
        overall_assessment = review_result.get('overall_assessment', {})
        
        ui.print_info(f"📊 整体评分: {overall_assessment.get('overall_score', 0)}/100")
        ui.print_info(f"🏆 评级: {overall_assessment.get('grade', '未知')}")
        ui.print_info(f"📝 总结: {overall_assessment.get('summary', '无')}")
        
        # 显示目标达成情况
        goal_achievement = review_result.get('goal_achievement', {})
        ui.print_info(f"🎯 目标达成度: {goal_achievement.get('achievement_percentage', 0)}%")
        
        # 显示问题列表
        issues = review_result.get('issues_identified', [])
        if issues:
            ui.print_warning(f"⚠️ 发现 {len(issues)} 个问题:")
            for issue in issues[:3]:  # 只显示前3个问题
                ui.print_info(f"   - {issue.get('description', '未知问题')}")
        
        # 显示改进建议
        suggestions = review_result.get('improvement_suggestions', [])
        if suggestions:
            ui.print_info(f"💡 改进建议:")
            for suggestion in suggestions[:3]:  # 只显示前3个建议
                ui.print_info(f"   - {suggestion.get('suggestion', '无建议')}")

    def start_session(self):
        """启动一个持续的交互会话"""
        ui.print_welcome_message()
        
        while True:
            user_input = ui.get_user_input()
            
            if not user_input:
                continue
                
            if user_input.lower() == 'exit':
                ui.print_info("👋 感谢使用 IntelliCLI！")
                break
            elif user_input.lower() == 'help':
                ui.print_help()
                continue
            elif user_input.lower() == 'clear':
                self.clear_session_memory()
                continue
            elif user_input.lower() == 'models':
                self.show_model_info()
                continue
            elif user_input.lower() == 'review':
                self._handle_review_command()
                continue
            elif user_input.lower() == 'history':
                self._handle_history_command()
                continue
            
            if not self.task_active:
                self.current_goal = user_input
                self.task_active = True
                ui.print_info(f"新任务: {self.current_goal}")
            
            # 尝试执行当前任务
            task_completed = self._run_task_iteration(self.current_goal)
            if task_completed:
                ui.print_task_completion()
                self.task_active = False
                self.current_goal = None

@app.command()
def chat(prompt: str, ctx: typer.Context):
    """与指定模型开始聊天会话。"""
    model_router = ctx.obj["model_router"]
    
    # 根据提示选择模型
    selected_model = model_router.route_task(prompt)
    model_client = model_router.get_model_client(selected_model)
    
    if not model_client:
        ui.print_error(f"无法获取模型客户端: {selected_model}")
        return
    
    ui.print_info(f"使用模型: {selected_model}")
    response = model_client.generate(prompt)
    print(response)

@app.command()
def task(
    prompt: str, 
    ctx: typer.Context,
    enable_review: bool = typer.Option(False, "--review", "-r", help="启用任务复盘功能")
):
    """
    执行复杂任务，支持规划、执行和复盘功能。
    """
    config = ctx.obj["config"]
    
    # 检查是否启用复盘功能
    review_config = config.get('task_review', {})
    should_review = enable_review or review_config.get('auto_review', False)
    
    if should_review and review_config.get('enabled', False):
        # 使用新的智能代理执行任务（支持复盘）
        primary_client = get_model_client(config)
        intelli_agent = IntelliAgent(primary_client, config)
        
        ui.print_section_header("IntelliCLI 智能任务执行", "🤖")
        ui.print_info(f"🎯 目标: {prompt}")
        
        result = intelli_agent.execute_task(prompt, enable_review=should_review)
        
        if result['status'] in ['completed', 'mostly_completed']:
            ui.print_success("✅ 任务成功完成！")
        else:
            ui.print_error("❌ 任务未能完成。")
    else:
        # 使用原有的Agent类执行任务
        agent = ctx.obj["agent"]
        agent.current_goal = prompt
        agent.task_active = True
        
        ui.print_section_header("IntelliCLI 任务执行", "🤖")
        ui.print_info(f"🎯 目标: {prompt}")
        
        success = agent._run_task_iteration(prompt)
        
        if success:
            ui.print_success("✅ 任务成功完成！")
        else:
            ui.print_error("❌ 任务未能完成。")
        
        agent.task_active = False

@app.command()
def session(ctx: typer.Context):
    """启动一个持续的 IntelliCLI 会话。"""
    # 使用原有的Agent类进行会话
    agent = ctx.obj["agent"]
    agent.start_session()

@app.command()
def models(ctx: typer.Context):
    """显示所有可用模型信息。"""
    model_router = ctx.obj["model_router"]
    models_info = model_router.list_available_models()
    
    ui.print_section_header("可用模型信息", "🧠")
    for alias, info in models_info.items():
        capabilities = ", ".join(info["capabilities"])
        ui.print_info(f"• {alias}: {info['model_name']} ({info['provider']}) - {capabilities}")
    
    # 验证配置并显示警告
    validation_result = model_router.validate_routing_rules()
    
    if validation_result.get("warnings"):
        ui.print_info("")
        ui.print_warning("⚠️ 配置建议:")
        for warning in validation_result["warnings"]:
            ui.print_info(f"  - {warning}")
        ui.print_info("")
        ui.print_info("💡 可以使用 'intellicli config-wizard' 重新配置模型")
    
    if not validation_result.get("valid"):
        ui.print_info("")
        ui.print_error("❌ 配置问题:")
        for issue in validation_result.get("issues", []):
            ui.print_info(f"  - {issue}")

@app.command()
def config():
    """显示当前模型配置"""
    try:
        config_manager = ModelConfigManager()
        config_manager.show_current_config()
    except Exception as e:
        ui.print_error(f"显示配置时出错: {e}")
        raise typer.Exit(code=1)

@app.command()
def config_wizard():
    """运行模型配置向导"""
    try:
        config_manager = ModelConfigManager()
        success = config_manager.run_config_wizard()
        if success:
            ui.print_success("✅ 配置向导完成！")
        else:
            ui.print_error("❌ 配置向导失败")
            raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"运行配置向导时出错: {e}")
        raise typer.Exit(code=1)

@app.command()
def config_reset():
    """重置模型配置"""
    try:
        config_manager = ModelConfigManager()
        success = config_manager.reconfigure()
        if success:
            ui.print_success("✅ 配置重置完成！")
        else:
            ui.print_error("❌ 配置重置失败")
            raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"重置配置时出错: {e}")
        raise typer.Exit(code=1)

@app.command(name="review-config")
def review_config():
    """配置复盘功能"""
    try:
        config_manager = ModelConfigManager()
        success = config_manager.configure_review_only()
        if not success:
            raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"配置复盘功能时出错: {e}")
        raise typer.Exit(code=1)

@app.command(name="search-config")
def search_config():
    """配置搜索引擎"""
    try:
        search_config_manager = SearchConfigManager()
        search_config_manager.run_config_wizard()
    except Exception as e:
        ui.print_error(f"配置搜索引擎时出错: {e}")
        raise typer.Exit(code=1)

@app.command(name="search-status")
def search_status():
    """显示搜索引擎配置状态"""
    try:
        search_config_manager = SearchConfigManager()
        search_config_manager.show_search_config()
    except Exception as e:
        ui.print_error(f"显示搜索配置时出错: {e}")
        raise typer.Exit(code=1)

@app.command()
def search_test(
    query: str = typer.Option("Python 编程", help="测试搜索查询"),
    engine: str = typer.Option("auto", help="指定搜索引擎 (auto, google, bing, yahoo, duckduckgo, startpage, searx)"),
    test_failover: bool = typer.Option(False, help="测试故障转移功能")
):
    """测试搜索引擎功能，包括智能切换"""
    from .tools.web_search import web_search, get_available_engines, search_health
    
    print("🔍 搜索引擎功能测试")
    print("=" * 50)
    print(f"查询: {query}")
    print(f"引擎: {engine}")
    print(f"测试故障转移: {'是' if test_failover else '否'}")
    
    if test_failover:
        print("\n🧪 故障转移测试模式")
        print("将模拟部分引擎失败，测试自动切换功能...")
        
        # 临时标记一些引擎为失败状态进行测试
        available_engines = get_available_engines()
        if len(available_engines) > 1:
            # 模拟第一个引擎失败
            test_engine = available_engines[0]
            print(f"🔧 模拟 {test_engine} 引擎失败...")
            search_health.record_failure(test_engine)
            search_health.record_failure(test_engine)
            search_health.record_failure(test_engine)  # 触发黑名单
    
    try:
        print(f"\n🚀 开始搜索...")
        result = web_search(query, engine, max_results=3)
        
        if "error" in result:
            print(f"❌ 搜索失败: {result['error']}")
            if "search_info" in result:
                search_info = result["search_info"]
                print(f"尝试的引擎: {search_info.get('engines_tried', [])}")
                print(f"总尝试次数: {search_info.get('total_attempts', 0)}")
        else:
            print(f"✅ 搜索成功!")
            
            # 显示搜索信息
            if "search_info" in result:
                search_info = result["search_info"]
                print(f"使用的引擎: {search_info['engine_used']}")
                print(f"尝试次数: {search_info['attempt_number']}/{search_info['total_attempts']}")
                if search_info.get('auto_switched'):
                    print("🔄 发生了自动切换")
            
            # 显示搜索结果
            print(f"\n📋 搜索结果 (共 {result.get('total_results', 0)} 条):")
            for i, item in enumerate(result.get("results", []), 1):
                print(f"\n{i}. {item.get('title', 'N/A')}")
                print(f"   链接: {item.get('url', 'N/A')}")
                snippet = item.get('snippet', 'N/A')
                if len(snippet) > 100:
                    snippet = snippet[:100] + "..."
                print(f"   摘要: {snippet}")
        
        # 显示当前健康状态
        print(f"\n📊 当前引擎健康状态:")
        available_engines = get_available_engines()
        print(f"可用引擎: {', '.join(available_engines) if available_engines else '无'}")
        
        # 显示失败统计
        if search_health.failure_counts:
            print("失败统计:")
            for engine, count in search_health.failure_counts.items():
                if count > 0:
                    print(f"  - {engine}: {count} 次")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

@app.command()
def search_health():
    """显示搜索引擎健康状态报告"""
    from .tools.web_search import get_search_health_report
    
    print("🔍 搜索引擎健康状态报告")
    print("=" * 50)
    
    try:
        report = get_search_health_report()
        
        # 显示可用引擎
        print(f"\n📊 可用引擎数量: {report['total_available']}")
        if report['available_engines']:
            print("✅ 可用引擎列表 (按优先级排序):")
            for i, engine in enumerate(report['available_engines'], 1):
                priority = report['engine_priorities'].get(engine, 'N/A')
                failure_count = report['failure_counts'].get(engine, 0)
                last_success = report['last_success'].get(engine, '从未成功')
                
                print(f"  {i}. {engine}")
                print(f"     优先级: {priority}")
                print(f"     失败次数: {failure_count}")
                print(f"     最后成功: {last_success}")
        else:
            print("❌ 当前没有可用的搜索引擎")
        
        # 显示黑名单引擎
        if report['blacklisted_engines']:
            print("\n🚫 暂时禁用的引擎:")
            for engine_info in report['blacklisted_engines']:
                print(f"  - {engine_info['engine']} (剩余 {engine_info['remaining_minutes']} 分钟)")
        
        # 显示失败统计
        if report['failure_counts']:
            print("\n📈 失败统计:")
            for engine, count in report['failure_counts'].items():
                if count > 0:
                    print(f"  - {engine}: {count} 次失败")
        
        print("\n💡 提示:")
        print("  - 引擎连续失败3次后会被暂时禁用5分钟")
        print("  - 优先级数字越小表示优先级越高")
        print("  - 使用 'intellicli search-test' 测试搜索功能")
        
    except Exception as e:
        print(f"❌ 获取健康状态报告时出错: {e}")

@app.command()
def review(
    goal: Optional[str] = typer.Option(None, "--goal", "-g", help="指定要复盘的任务目标"),
    auto_fix: bool = typer.Option(False, "--auto-fix", "-f", help="自动执行补充计划")
):
    """
    对任务执行结果进行复盘分析
    """
    try:
        config = load_config()
        
        # 检查复盘功能是否启用
        review_config = config.get('task_review', {})
        if not review_config.get('enabled', False):
            ui.print_review_disabled()
            return
        
        # 初始化模型客户端
        primary_client = get_model_client(config)
        
        # 创建智能代理
        agent = IntelliAgent(primary_client, config)
        
        # 执行手动复盘
        if goal:
            ui.print_info(f"🔍 开始复盘任务: {goal}")
        else:
            ui.print_info("🔍 开始复盘最近的任务")
        
        review_result = agent.manual_review(goal)
        
        if review_result:
            ui.print_success("✅ 复盘完成")
        else:
            ui.print_warning("⚠️ 复盘未找到相关任务")
            
    except Exception as e:
        ui.print_error(f"复盘过程中出错: {e}")
        raise typer.Exit(code=1)

@app.command()
def history():
    """
    显示任务执行历史
    """
    try:
        config = load_config()
        primary_client = get_model_client(config)
        
        # 创建智能代理
        agent = IntelliAgent(primary_client, config)
        
        # 获取执行历史
        history = agent.get_execution_history()
        
        # 使用新的UI函数显示历史
        ui.print_task_history(history)
            
    except Exception as e:
        ui.print_error(f"获取历史记录时出错: {e}")
        raise typer.Exit(code=1)

@app.callback()
def callback(ctx: typer.Context):
    """
    IntelliCLI: 一个智能 CLI 助手，具有可插拔模型和动态任务规划。
    """
    config = load_config()
    
    # 初始化所有模型客户端
    model_clients = get_model_clients(config)
    
    if not model_clients:
        ui.print_error("❌ 未能初始化任何模型客户端，请检查配置")
        raise typer.Exit(1)
    
    # 创建智能模型路由器
    model_router = ModelRouter(model_clients, config)
    
    # 使用主模型创建规划器（后续会动态更新）
    primary_model = config.get('models', {}).get('primary', list(model_clients.keys())[0])
    primary_client = model_clients.get(primary_model)
    
    planner = Planner(primary_client)
    executor = Executor(model_client=primary_client)  # 传递主模型客户端给executor
    agent = Agent(model_router, planner, executor)
    
    ctx.obj = {
        "config": config,
        "model_router": model_router,
        "model_clients": model_clients,
        "planner": planner,
        "executor": executor,
        "agent": agent
    }

def main():
    """主入口点函数，供 pyproject.toml 使用"""
    app()

if __name__ == "__main__":
    main()