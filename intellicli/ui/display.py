"""
现代化的CLI用户界面模块
参考Gemini CLI的设计理念，提供优雅的命令行交互体验
"""

import sys
from typing import List, Dict, Any
from dataclasses import dataclass
import time

# 导入 prompt_toolkit 相关模块
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText

# ANSI颜色代码
class Colors:
    # 基础颜色
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 明亮颜色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 背景色
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

@dataclass
class UIConfig:
    """UI配置选项"""
    use_colors: bool = True
    show_timestamps: bool = False
    compact_mode: bool = False
    animation_speed: float = 0.05
    enable_history: bool = True
    enable_completion: bool = True

class ModernUI:
    """现代化的CLI用户界面"""
    
    def __init__(self, config: UIConfig = None):
        self.config = config or UIConfig()
        self._current_section = None
        self._step_start_time = None  # 添加步骤开始时间追踪
        
        # 初始化输入历史记录
        self.input_history = InMemoryHistory()
        
        # 初始化自动补全
        self.completer = WordCompleter([
            'help', 'exit', 'clear', 'models',
            '创建', '列出', '运行', '分析', '删除', '修改',
            '文件', '目录', '代码', '脚本', '网页', '图片'
        ])
        
        # 定义 prompt_toolkit 的样式
        self.prompt_style = Style.from_dict({
            'prompt': 'ansibrightcyan bold',
            'input': 'ansiwhite',
            'warning': 'ansibrightyellow',
            'error': 'ansibrightred',
            'success': 'ansibrightgreen',
        })
        
    def _colorize(self, text: str, color: str) -> str:
        """给文本添加颜色"""
        if not self.config.use_colors:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def _print(self, text: str, color: str = "", end: str = "\n"):
        """打印带颜色的文本"""
        colored_text = self._colorize(text, color) if color else text
        print(colored_text, end=end)
        sys.stdout.flush()
    
    def _animate_text(self, text: str, color: str = ""):
        """动画显示文本"""
        if not self.config.use_colors:
            print(text)
            return
            
        for char in text:
            self._print(char, color, end="")
            time.sleep(self.config.animation_speed)
        print()  # 换行
    
    def print_banner(self):
        """显示IntelliCLI横幅"""
        banner = """
+===============================================================================+
|                                                                               |
|  ██╗███╗   ██╗████████╗███████╗██╗     ██╗     ██╗ ██████╗██╗     ██╗         |
|  ██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ██║██╔════╝██║     ██║         |
|  ██║██╔██╗ ██║   ██║   █████╗  ██║     ██║     ██║██║     ██║     ██║         |
|  ██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║     ██║██║     ██║     ██║         |
|  ██║██║ ╚████║   ██║   ███████╗███████╗███████╗██║╚██████╗███████╗██║         |
|  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝╚══════╝╚═╝         |
|                                                                               |
|                     🚀 IntelliCLI 智能命令行助手 v1.1.0                       |
|                        让AI为你规划和执行任务                                 |
|                                                                               |
+===============================================================================+
        """
        self._print(banner, Colors.BRIGHT_CYAN)
    
    def print_welcome_message(self):
        """显示欢迎信息"""
        self.print_banner()
        
        welcome_text = [
            "",
            f"{Colors.BRIGHT_WHITE}🚀 欢迎使用 IntelliCLI！{Colors.RESET}",
            "",
            "📝 输入您的任务，AI 将为您智能规划和执行",
            "🔄 支持多步骤任务和自动错误恢复",
            "💡 具备会话记忆和上下文理解能力",
            "",
            f"{Colors.DIM}💡 提示：输入 '{Colors.BRIGHT_YELLOW}exit{Colors.DIM}' 退出会话{Colors.RESET}",
            f"{Colors.DIM}📚 输入 '{Colors.BRIGHT_YELLOW}help{Colors.DIM}' 查看帮助信息{Colors.RESET}",
            ""
        ]
        
        for line in welcome_text:
            self._print(line)
    
    def print_section_header(self, title: str, icon: str = "📋"):
        """显示区块标题"""
        if not self.config.compact_mode:
            self._print("")
        
        header = f"{icon} {title}"
        separator = "-" * (len(header) + 4)
        
        self._print(f"+--{separator}--+", Colors.BRIGHT_BLUE)
        self._print(f"|  {self._colorize(header, Colors.BRIGHT_WHITE)}  |", Colors.BRIGHT_BLUE)
        self._print(f"+--{separator}--+", Colors.BRIGHT_BLUE)
        
        if not self.config.compact_mode:
            self._print("")
    
    def print_planning_attempt(self, attempt: int, max_attempts: int):
        """显示规划尝试信息"""
        icon = "🎯" if attempt == 1 else "🔄"
        status = "初次规划" if attempt == 1 else f"重新规划 ({attempt-1}次重试)"
        
        self.print_section_header(f"代理规划尝试 {attempt}/{max_attempts}", icon)
        self._print(f"   {status}...", Colors.BRIGHT_YELLOW)
    
    def print_plan(self, plan: List[Dict[str, Any]]):
        """显示生成的计划"""
        self.print_section_header("生成的执行计划", "📋")
        
        for i, task in enumerate(plan, 1):
            tool = task.get('tool', '未知工具')
            args = task.get('arguments', {})
            
            # 简化参数显示
            simplified_args = {}
            for key, value in args.items():
                if isinstance(value, str) and len(value) > 50:
                    simplified_args[key] = value[:47] + "..."
                else:
                    simplified_args[key] = value
            
            step_icon = "🔧"
            self._print(f"   {step_icon} 步骤 {i}: ", Colors.BRIGHT_GREEN, end="")
            self._print(f"{tool}", Colors.BRIGHT_WHITE, end="")
            
            if simplified_args:
                self._print(f" → {simplified_args}", Colors.DIM)
            else:
                self._print("")
    
    def print_execution_header(self):
        """显示执行开始信息"""
        self.print_section_header("开始执行计划", "⚡")
    
    def print_step_execution(self, step: int, total: int, tool: str, status: str = "running"):
        """显示步骤执行状态"""
        status_icons = {
            "running": "⏳",
            "success": "✅",
            "failed": "❌"
        }
        
        status_colors = {
            "running": Colors.BRIGHT_YELLOW,
            "success": Colors.BRIGHT_GREEN,
            "failed": Colors.BRIGHT_RED
        }
        
        icon = status_icons.get(status, "⏳")
        color = status_colors.get(status, Colors.BRIGHT_YELLOW)
        
        step_text = f"   {icon} 步骤 {step}/{total}: {tool}"
        
        if status == "running":
            self._print(step_text + "...", color)
        else:
            self._print(step_text, color)
    
    def print_step_result(self, result: str, is_error: bool = False):
        """显示步骤结果"""
        if is_error:
            self._print(f"      ❌ 错误: {result}", Colors.BRIGHT_RED)
        else:
            # 限制结果显示长度
            display_result = result if len(result) <= 100 else result[:97] + "..."
            self._print(f"      📄 结果: {display_result}", Colors.DIM)
    
    def print_execution_summary(self, total: int, success: int, failed: int):
        """显示执行摘要"""
        if not self.config.compact_mode:
            self._print("")
        
        if failed == 0:
            icon = "🎉"
            message = "所有步骤执行成功！"
            color = Colors.BRIGHT_GREEN
        else:
            icon = "⚠️"
            message = f"发现 {failed} 个失败步骤"
            color = Colors.BRIGHT_YELLOW
        
        self._print(f"   {icon} 执行完成：{message}", color)
        self._print(f"      总步骤: {total} | 成功: {success} | 失败: {failed}", Colors.DIM)
    
    def print_task_completion(self):
        """显示任务完成信息"""
        completion_message = [
            "",
            f"🎊 {self._colorize('任务完成！', Colors.BRIGHT_GREEN)}",
            f"   {self._colorize('您可以输入新任务或输入 exit 退出', Colors.DIM)}",
            f"   {self._colorize('💡 提示：可以使用 review 命令手动复盘此次任务', Colors.BRIGHT_BLUE)}",
            ""
        ]
        
        for line in completion_message:
            self._print(line)
    
    def print_review_header(self, success_rate: float, threshold: float):
        """显示复盘开始信息"""
        self.print_section_header("任务复盘", "🔍")
        self._print(f"开始复盘分析（成功率: {success_rate:.1f}%，阈值: {threshold:.1f}%）", Colors.BRIGHT_YELLOW)
    
    def print_review_result(self, review_result: Dict[str, Any]):
        """显示复盘结果"""
        # 显示整体评分
        overall_score = review_result.get('overall_score', 0)
        grade = review_result.get('grade', '未知')
        summary = review_result.get('summary', '无摘要')
        
        score_color = Colors.BRIGHT_GREEN if overall_score >= 80 else Colors.BRIGHT_YELLOW if overall_score >= 60 else Colors.BRIGHT_RED
        
        self._print(f"📊 整体评分: {overall_score}/100", score_color)
        self._print(f"🏆 评级: {grade}", score_color)
        self._print(f"📝 总结: {summary}", Colors.BRIGHT_WHITE)
        
        # 显示目标达成度
        if 'goal_achievement' in review_result:
            goal_score = review_result['goal_achievement']
            self._print(f"🎯 目标达成度: {goal_score}%", Colors.BRIGHT_CYAN)
        
        # 显示发现的问题
        issues = review_result.get('issues', [])
        if issues:
            self._print(f"⚠️ 发现 {len(issues)} 个问题:", Colors.BRIGHT_YELLOW)
            for issue in issues:
                self._print(f"   - {issue}", Colors.YELLOW)
        
        # 显示改进建议
        suggestions = review_result.get('suggestions', [])
        if suggestions:
            self._print(f"💡 改进建议:", Colors.BRIGHT_BLUE)
            for suggestion in suggestions:
                self._print(f"   - {suggestion}", Colors.BLUE)
    
    def print_review_improvement(self, iteration: int):
        """显示复盘改进信息"""
        self.print_section_header("执行补充计划", "🔧")
        self._print(f"第 {iteration} 次改进迭代", Colors.BRIGHT_YELLOW)
    
    def print_review_improvement_success(self, iteration: int):
        """显示改进成功信息"""
        self._print(f"✅ 第 {iteration} 次改进成功！", Colors.BRIGHT_GREEN)
    
    def print_review_improvement_failed(self, iteration: int, error: str):
        """显示改进失败信息"""
        self._print(f"❌ 第 {iteration} 次改进失败: {error}", Colors.BRIGHT_RED)
    
    def print_review_final_result(self, final_success_rate: float, iterations: int):
        """显示最终复盘结果"""
        self._print("", Colors.RESET)
        if final_success_rate >= 0.8:
            self._print(f"🎉 复盘改进完成！最终成功率: {final_success_rate:.1f}% (共 {iterations} 次迭代)", Colors.BRIGHT_GREEN)
        else:
            self._print(f"⚠️ 复盘改进结束，最终成功率: {final_success_rate:.1f}% (共 {iterations} 次迭代)", Colors.BRIGHT_YELLOW)
    
    def print_review_disabled(self):
        """显示复盘功能未启用信息"""
        self._print("💡 复盘功能未启用。要启用复盘功能，请运行:", Colors.BRIGHT_BLUE)
        self._print("   intellicli review-config", Colors.BRIGHT_CYAN)
        self._print("   或编辑 config.yaml 文件设置 task_review.enabled: true", Colors.BRIGHT_CYAN)
    
    def print_review_config_status(self, enabled: bool, auto_review: bool, threshold: float, max_iterations: int):
        """显示复盘配置状态"""
        self._print("📋 复盘功能配置状态:", Colors.BRIGHT_BLUE)
        self._print(f"   启用状态: {'✅ 是' if enabled else '❌ 否'}", Colors.BRIGHT_GREEN if enabled else Colors.BRIGHT_RED)
        if enabled:
            self._print(f"   自动复盘: {'✅ 是' if auto_review else '❌ 否'}", Colors.BRIGHT_GREEN if auto_review else Colors.BRIGHT_YELLOW)
            self._print(f"   复盘阈值: {threshold}", Colors.BRIGHT_CYAN)
            self._print(f"   最大迭代: {max_iterations}", Colors.BRIGHT_CYAN)
    
    def print_task_history(self, history: List[Dict[str, Any]]):
        """显示任务执行历史"""
        if not history:
            self._print("📋 暂无任务执行历史", Colors.BRIGHT_YELLOW)
            return
        
        self.print_section_header("任务执行历史", "📚")
        
        for i, task in enumerate(history, 1):
            goal = task.get('goal', '未知任务')
            success_rate = task.get('success_rate', 0)
            reviewed = task.get('reviewed', False)
            timestamp = task.get('timestamp', '未知时间')
            
            # 根据成功率选择图标和颜色
            if success_rate >= 90:
                icon = "✅"
                color = Colors.BRIGHT_GREEN
            elif success_rate >= 70:
                icon = "🟡"
                color = Colors.BRIGHT_YELLOW
            else:
                icon = "❌"
                color = Colors.BRIGHT_RED
            
            review_status = "🔍" if reviewed else "⏸️"
            
            self._print(f"{i}. {icon} {goal}", color)
            self._print(f"   成功率: {success_rate:.1f}% | 复盘: {review_status}", Colors.DIM)
            self._print(f"   时间: {timestamp}", Colors.DIM)
            self._print("", Colors.RESET)
    
    def print_error(self, error_message: str):
        """显示错误信息"""
        self._print(f"❌ 错误: {error_message}", Colors.BRIGHT_RED)
    
    def print_warning(self, warning_message: str):
        """显示警告信息"""
        self._print(f"⚠️  警告: {warning_message}", Colors.BRIGHT_YELLOW)
    
    def print_info(self, info_message: str):
        """显示信息"""
        self._print(f"💡 {info_message}", Colors.BRIGHT_BLUE)
    
    def print_success(self, success_message: str):
        """显示成功信息"""
        self._print(f"✅ {success_message}", Colors.BRIGHT_GREEN)
    
    def get_user_input(self, prompt_text: str = "IntelliCLI") -> str:
        """获取用户输入 - 支持方向键和正确的中文处理"""
        try:
            # 创建格式化的提示符
            formatted_prompt = FormattedText([
                ('class:prompt', f"{prompt_text}: "),
            ])
            
            # 使用 prompt_toolkit 获取输入
            user_input = prompt(
                formatted_prompt,
                style=self.prompt_style,
                history=self.input_history if self.config.enable_history else None,
                completer=self.completer if self.config.enable_completion else None,
                complete_while_typing=True,
                vi_mode=False,  # 使用 Emacs 模式，支持常见的快捷键
                multiline=False,
                wrap_lines=True,
                mouse_support=True,
                enable_history_search=True,
            )
            
            return user_input.strip()
            
        except KeyboardInterrupt:
            print_formatted_text(FormattedText([
                ('class:warning', '\n👋 用户取消操作')
            ]))
            return ""
        except EOFError:
            print_formatted_text(FormattedText([
                ('class:warning', '\n👋 会话结束')
            ]))
            return "exit"
        except Exception as e:
            # 如果 prompt_toolkit 出现问题，回退到基本的 input()
            print(f"⚠️  输入系统错误，回退到基本模式: {e}")
            try:
                prompt_basic = f"{self._colorize(prompt_text, Colors.BRIGHT_CYAN)}: "
                return input(prompt_basic).strip()
            except (KeyboardInterrupt, EOFError):
                return "exit"
    
    def print_help(self):
        """显示帮助信息"""
        help_text = f"""
{self._colorize("📖 IntelliCLI 帮助", Colors.BRIGHT_CYAN)}
{self._colorize("=" * 50, Colors.CYAN)}

{self._colorize("🚀 基本命令:", Colors.BRIGHT_YELLOW)}
  {self._colorize("task <描述>", Colors.WHITE)}         - 执行复杂任务
  {self._colorize("chat <问题>", Colors.WHITE)}         - 与AI聊天
  {self._colorize("session", Colors.WHITE)}             - 启动交互会话

{self._colorize("⚙️  配置命令:", Colors.BRIGHT_YELLOW)}
  {self._colorize("config", Colors.WHITE)}              - 显示当前配置
  {self._colorize("config-wizard", Colors.WHITE)}       - 运行配置向导
  {self._colorize("config-edit", Colors.WHITE)}         - 直接编辑配置文件
  {self._colorize("config-reset", Colors.WHITE)}        - 重置配置
  {self._colorize("review-config", Colors.WHITE)}       - 配置复盘功能
  {self._colorize("search-config", Colors.WHITE)}       - 配置搜索引擎
  {self._colorize("mcp-config", Colors.WHITE)}          - 配置MCP服务器

{self._colorize("🔍 搜索相关:", Colors.BRIGHT_YELLOW)}
  {self._colorize("search-status", Colors.WHITE)}       - 显示搜索引擎状态
  {self._colorize("search-test", Colors.WHITE)}         - 测试搜索功能
  {self._colorize("search-health", Colors.WHITE)}       - 显示搜索引擎健康状态

{self._colorize("🔧 MCP相关:", Colors.BRIGHT_YELLOW)}
  {self._colorize("mcp-status", Colors.WHITE)}          - 显示MCP服务器状态
  {self._colorize("mcp-tools", Colors.WHITE)}           - 显示可用MCP工具
  {self._colorize("mcp-refresh", Colors.WHITE)}         - 刷新MCP工具列表

{self._colorize("🔍 复盘相关:", Colors.BRIGHT_YELLOW)}
  {self._colorize("review", Colors.WHITE)}              - 复盘任务执行结果
  {self._colorize("history", Colors.WHITE)}             - 显示任务执行历史

{self._colorize("ℹ️  信息命令:", Colors.BRIGHT_YELLOW)}
  {self._colorize("models", Colors.WHITE)}              - 显示可用模型

{self._colorize("💬 会话命令 (在session模式中):", Colors.BRIGHT_YELLOW)}
  {self._colorize("help", Colors.WHITE)}                - 显示帮助
  {self._colorize("clear", Colors.WHITE)}               - 清空会话记忆
  {self._colorize("models", Colors.WHITE)}              - 显示模型信息
  {self._colorize("review", Colors.WHITE)}              - 复盘最近任务
  {self._colorize("history", Colors.WHITE)}             - 显示执行历史
  {self._colorize("exit", Colors.WHITE)}                - 退出会话

{self._colorize("💡 配置文件说明:", Colors.BRIGHT_GREEN)}
• {self._colorize("config-wizard", Colors.WHITE)} - 完整配置向导，现在会询问是否保留现有配置
• {self._colorize("config-edit", Colors.WHITE)} - 直接编辑config.yaml文件，支持多种编辑器
• {self._colorize("各专项配置", Colors.WHITE)} - 只更新对应部分，不会覆盖其他配置

{self._colorize("📝 配置文件结构:", Colors.BRIGHT_GREEN)}
• models - 模型配置
• search_engines - 搜索引擎配置  
• mcp_servers - MCP服务器配置
• task_review - 复盘功能配置
• tools - 工具配置

{self._colorize("🔧 MCP Chrome 自定义配置示例:", Colors.BRIGHT_GREEN)}
要配置自定义MCP服务器（如Chrome Tools），请在配置文件中添加：

```yaml
mcp_servers:
  servers:
  - name: mcp_chrome_tools
    command: [npx, '@nicholmikey/chrome-tools@latest']
    args: ['-y']
    description: Chrome浏览器自动化工具
    enabled: true
    auto_restart: true
    env:
      CHROME_DEBUG_URL: 'http://localhost:9222'
```

{self._colorize("🚀 启动Chrome调试模式:", Colors.BRIGHT_GREEN)}
macOS: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222
Windows: chrome.exe --remote-debugging-port=9222
Linux: google-chrome --remote-debugging-port=9222

更多信息请访问: https://github.com/IntelliCLI/IntelliCLI
"""
        print(help_text)

    def print_step_execution_enhanced(self, step: int, total: int, tool: str, model: str = None):
        """显示增强的步骤执行状态"""
        # 记录步骤开始时间
        self._step_start_time = time.time()
        
        # 创建进度条
        progress_bar = self._create_progress_bar(step, total)
        
        # 显示步骤信息
        self._print(f"\n{progress_bar}", Colors.BRIGHT_BLUE)
        self._print(f"   ⏳ 步骤 {step}/{total}: {tool}...", Colors.BRIGHT_YELLOW)
        
        if model:
            self._print(f"💡   🤖 执行模型: {model}", Colors.DIM)
        
        # 显示开始时间
        start_time_str = time.strftime('%H:%M:%S', time.localtime(self._step_start_time))
        self._print(f"      📍 开始时间: {start_time_str}", Colors.DIM)
    
    def print_step_completion_enhanced(self, step: int, total: int, tool: str, result: str, is_error: bool = False):
        """显示增强的步骤完成状态"""
        # 计算执行时间
        execution_time = 0
        if self._step_start_time:
            execution_time = time.time() - self._step_start_time
        
        # 创建进度条
        progress_bar = self._create_progress_bar(step, total)
        
        if is_error:
            self._print(f"   ❌ 步骤 {step}/{total}: {tool}", Colors.BRIGHT_RED)
            self._print(f"      ❌ 错误: {result}", Colors.BRIGHT_RED)
        else:
            self._print(f"   ✅ 步骤 {step}/{total}: {tool}", Colors.BRIGHT_GREEN)
            # 限制结果显示长度
            display_result = result if len(result) <= 100 else result[:97] + "..."
            self._print(f"      📄 结果: {display_result}", Colors.DIM)
        
        # 显示执行时间
        self._print(f"      ⏱️ 执行时间: {execution_time:.2f}s", Colors.DIM)
        
        # 重置开始时间
        self._step_start_time = None
    
    def _create_progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """创建进度条"""
        progress = current / total
        filled_width = int(width * progress)
        
        # 创建进度条
        bar = "█" * filled_width + "▒" * (width - filled_width)
        percentage = int(progress * 100)
        
        return f"   🔄 进度: [{bar}] {percentage}% ({current}/{total})"
    
    def print_command_execution_start(self, command: str):
        """显示命令开始执行"""
        self._print(f"      🔄 正在执行: {command}", Colors.BRIGHT_CYAN)
        self._print(f"      📍 开始时间: {time.strftime('%H:%M:%S')}", Colors.DIM)
    
    def print_command_real_time_output(self, output: str):
        """显示命令实时输出"""
        if output.strip():
            self._print(f"      📝 {output.strip()}", Colors.WHITE)
    
    def print_command_execution_complete(self, success: bool, execution_time: float, return_code: int = 0):
        """显示命令执行完成"""
        if success:
            self._print(f"      ✅ 命令执行成功 (耗时: {execution_time:.2f}s)", Colors.BRIGHT_GREEN)
        else:
            self._print(f"      ❌ 命令执行失败 (返回码: {return_code}, 耗时: {execution_time:.2f}s)", Colors.BRIGHT_RED)
    
    def print_long_running_task_warning(self, task_name: str, timeout: int = 300):
        """显示长时间运行任务的警告"""
        self._print(f"      ⚠️  长时间任务警告: {task_name}", Colors.BRIGHT_YELLOW)
        self._print(f"      ⏰ 预计可能需要较长时间执行，请耐心等待...", Colors.YELLOW)
        self._print(f"      💡 提示: 如果超过 {timeout}s 仍未完成，可以考虑中断任务", Colors.DIM)
    
    def show_spinner_with_message(self, message: str, duration: float = 1.0):
        """显示带消息的旋转器"""
        spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            sys.stdout.write(f"\r      {spinners[i]} {message} ({elapsed:.1f}s)")
            sys.stdout.flush()
            i = (i + 1) % len(spinners)
            time.sleep(0.1)
        
        # 清除spinner
        sys.stdout.write('\r' + ' ' * (len(message) + 20) + '\r')
        sys.stdout.flush()
    
    def print_execution_stats(self, total_time: float, steps_executed: int, success_count: int, failure_count: int):
        """显示执行统计信息"""
        self._print("")
        self.print_section_header("执行统计", "📊")
        
        # 成功率计算
        success_rate = (success_count / steps_executed * 100) if steps_executed > 0 else 0
        
        # 选择状态颜色
        if success_rate >= 90:
            status_color = Colors.BRIGHT_GREEN
            status_icon = "🎉"
        elif success_rate >= 70:
            status_color = Colors.BRIGHT_YELLOW
            status_icon = "⚠️"
        else:
            status_color = Colors.BRIGHT_RED
            status_icon = "❌"
        
        self._print(f"   {status_icon} 整体成功率: {success_rate:.1f}%", status_color)
        self._print(f"   📈 执行步骤: {steps_executed}", Colors.BRIGHT_WHITE)
        self._print(f"   ✅ 成功步骤: {success_count}", Colors.BRIGHT_GREEN)
        self._print(f"   ❌ 失败步骤: {failure_count}", Colors.BRIGHT_RED)
        self._print(f"   ⏱️ 总执行时间: {total_time:.2f}s", Colors.BRIGHT_CYAN)
        self._print(f"   📊 平均每步时间: {total_time/steps_executed:.2f}s", Colors.DIM)

    def print_interactive_prompt(self, command: str, prompt_text: str):
        """显示交互式输入提示"""
        self._print("")
        self._print(f"      🔄 命令需要用户交互:", Colors.BRIGHT_YELLOW)
        self._print(f"      📝 提示信息: {prompt_text}", Colors.WHITE)
        self._print(f"      💡 请直接在下方输入响应:", Colors.BRIGHT_BLUE)
        self._print(f"      " + "="*60, Colors.DIM)
    
    def print_interactive_input_received(self, user_input: str):
        """显示已接收的用户输入"""
        self._print(f"      ✅ 已发送输入: {user_input}", Colors.BRIGHT_GREEN)
        self._print(f"      🔄 继续执行命令...", Colors.BRIGHT_YELLOW)
        self._print(f"      " + "="*60, Colors.DIM)
    
    def print_interactive_warning(self):
        """显示交互模式警告"""
        self._print(f"      ⚠️  检测到长时间无响应的命令", Colors.BRIGHT_YELLOW)
        self._print(f"      💡 可能需要用户交互，请检查命令输出", Colors.BRIGHT_BLUE)
        self._print(f"      🔄 如需交互，请直接在终端中操作", Colors.DIM)
    
    def print_command_waiting_input(self, waiting_time: float):
        """显示命令等待输入状态"""
        self._print(f"      ⏳ 命令等待用户输入 (已等待: {waiting_time:.1f}s)", Colors.BRIGHT_YELLOW)
    
    def print_interactive_mode_detected(self, trigger: str):
        """显示检测到交互模式"""
        self._print(f"      🔍 交互检测: {trigger}", Colors.BRIGHT_CYAN)
        self._print(f"      💬 准备接收用户输入...", Colors.BRIGHT_BLUE)

# 全局UI实例
ui = ModernUI() 