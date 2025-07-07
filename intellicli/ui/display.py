"""
现代化的CLI用户界面模块
参考Gemini CLI的设计理念，提供优雅的命令行交互体验
"""

import sys
from typing import List, Dict, Any
from dataclasses import dataclass
import time

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

class ModernUI:
    """现代化的CLI用户界面"""
    
    def __init__(self, config: UIConfig = None):
        self.config = config or UIConfig()
        self._current_section = None
        
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
╭─────────────────────────────────────────────────────────────╮
│                                                             │
│  ██╗███╗   ██╗████████╗███████╗██╗     ██╗     ██╗ ██████╗ │
│  ██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ██║██╔════╝ │
│  ██║██╔██╗ ██║   ██║   █████╗  ██║     ██║     ██║██║      │
│  ██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║     ██║██║      │
│  ██║██║ ╚████║   ██║   ███████╗███████╗███████╗██║╚██████╗ │
│  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ │
│                                                             │
│           智能命令行助手 - 让AI为你规划和执行任务             │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
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
        separator = "─" * (len(header) + 4)
        
        self._print(f"╭─{separator}─╮", Colors.BRIGHT_BLUE)
        self._print(f"│  {self._colorize(header, Colors.BRIGHT_WHITE)}  │", Colors.BRIGHT_BLUE)
        self._print(f"╰─{separator}─╯", Colors.BRIGHT_BLUE)
        
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
            ""
        ]
        
        for line in completion_message:
            self._print(line)
    
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
    
    def get_user_input(self, prompt: str = "IntelliCLI") -> str:
        """获取用户输入"""
        prompt_text = f"{self._colorize(prompt, Colors.BRIGHT_CYAN)}: "
        try:
            return input(prompt_text).strip()
        except KeyboardInterrupt:
            self._print("\n")
            self._print("👋 用户取消操作", Colors.BRIGHT_YELLOW)
            return ""
        except EOFError:
            self._print("\n")
            self._print("👋 会话结束", Colors.BRIGHT_YELLOW)
            return "exit"
    
    def print_help(self):
        """显示帮助信息"""
        help_text = [
            "",
            f"{Colors.BRIGHT_WHITE}📚 IntelliCLI 帮助信息{Colors.RESET}",
            "",
            "🔤 基本命令:",
            f"   • {Colors.BRIGHT_YELLOW}help{Colors.RESET} - 显示此帮助信息",
            f"   • {Colors.BRIGHT_YELLOW}exit{Colors.RESET} - 退出 IntelliCLI",
            f"   • {Colors.BRIGHT_YELLOW}clear{Colors.RESET} - 清空会话记忆",
            f"   • {Colors.BRIGHT_YELLOW}models{Colors.RESET} - 显示可用模型信息",
            "",
            "🧠 智能模型路由:",
            "   • 系统会根据任务类型自动选择最合适的模型",
            "   • 🖼️  图像任务 → 视觉模型 (LLaVA, Gemini Vision)",
            "   • 💻 代码任务 → 代码模型 (Gemini, Gemma)",
            "   • 🤔 推理任务 → 推理模型 (Gemini, Gemma)",
            "   • 💬 一般任务 → 通用模型 (Gemma, Gemini)",
            "",
            "💡 使用技巧:",
            "   • 直接描述您想完成的任务",
            "   • 支持文件操作、代码分析、系统命令等",
            "   • AI 会自动规划多个步骤来完成复杂任务",
            "   • 具备上下文记忆，可以理解连续的任务",
            "   • 涉及图像的任务会自动使用视觉模型",
            "",
            "🎯 示例任务:",
            "   • 创建一个简单的网页",
            "   • 分析Python代码的第一个函数",
            "   • 列出当前目录的文件",
            "   • 运行刚创建的HTML文件",
            "   • 识别截图中的内容 (自动使用视觉模型)",
            "   • 编写复杂的算法 (自动使用代码模型)",
            ""
        ]
        
        for line in help_text:
            self._print(line)

# 全局UI实例
ui = ModernUI() 