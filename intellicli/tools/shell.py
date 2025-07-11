import subprocess
import threading
import time
import sys
import os
from typing import Optional, Callable

def run_shell_command(command: str, 
                     show_output: bool = True, 
                     progress_callback: Optional[Callable] = None,
                     timeout: Optional[int] = None,
                     interactive: bool = True) -> str:
    """
    执行 shell 命令并返回输出，完全透明执行（和直接在终端运行一样）。
    
    Args:
        command: 要执行的shell命令
        show_output: 是否实时显示输出
        progress_callback: 进度回调函数
        timeout: 超时时间（秒）
        interactive: 是否允许直接用户交互
    
    Returns:
        命令的完整输出
    """
    try:
        if interactive and hasattr(os, 'openpty'):
            # Unix系统使用pty - 完全透明执行
            return _handle_interactive_command_transparent(command, show_output, progress_callback)
        else:
            # 非交互模式或Windows系统
            return _handle_non_interactive_command_simple(command, show_output, progress_callback)
            
    except Exception as e:
        return f"执行命令时出错: {e}"

def _handle_interactive_command_transparent(command: str, show_output: bool, progress_callback: Optional[Callable]) -> str:
    """完全透明的交互式命令执行（就像直接在终端运行）"""
    import pty
    import select
    
    output_lines = []
    
    # 创建伪终端
    master, slave = pty.openpty()
    
    try:
        # 启动进程，连接到伪终端
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            text=True,
            close_fds=True
        )
        
        # 关闭slave端，我们只使用master端
        os.close(slave)
        
        # 完全透明的I/O处理 - 无任何进度指示器
        try:
            while True:
                # 检查进程是否结束
                if process.poll() is not None:
                    # 读取最后的输出
                    try:
                        while True:
                            data = os.read(master, 1024).decode('utf-8', errors='ignore')
                            if not data:
                                break
                            for line in data.split('\n'):
                                if line.strip():
                                    output_lines.append(line.strip())
                                if show_output:
                                    sys.stdout.write(f"{line}\n")
                                    sys.stdout.flush()
                    except OSError:
                        pass
                    break
                
                # 使用select检查I/O
                ready, _, _ = select.select([master, sys.stdin], [], [], 0.1)
                
                if master in ready:
                    # 从命令读取输出
                    try:
                        data = os.read(master, 1024).decode('utf-8', errors='ignore')
                        if data:
                            # 直接显示输出，完全透明
                            lines = data.split('\n')
                            for i, line in enumerate(lines):
                                if i == len(lines) - 1 and line and not data.endswith('\n'):
                                    # 未完成的行，直接显示
                                    if show_output:
                                        sys.stdout.write(f"{line}")
                                        sys.stdout.flush()
                                else:
                                    # 完整的行
                                    if line.strip():
                                        output_lines.append(line.strip())
                                    if show_output:
                                        sys.stdout.write(f"{line}\n")
                                        sys.stdout.flush()
                            
                            # 调用进度回调
                            if progress_callback and output_lines:
                                progress_callback(output_lines[-1])
                    except OSError:
                        break
                
                if sys.stdin in ready:
                    # 用户输入，直接转发
                    try:
                        user_input = sys.stdin.readline()
                        os.write(master, user_input.encode('utf-8'))
                    except OSError:
                        break
        
        except KeyboardInterrupt:
            # 用户中断
            process.terminate()
        
        # 等待进程结束
        return_code = process.wait()
        
    finally:
        os.close(master)
    
    # 完整输出
    full_output = '\n'.join(output_lines)
    
    if return_code == 0:
        return full_output
    else:
        return f"执行命令时出错 (返回码: {return_code}): {full_output}"

def _handle_non_interactive_command_simple(command: str, show_output: bool, progress_callback: Optional[Callable]) -> str:
    """简化的非交互式命令处理 - 完全透明"""
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    output_lines = []
    
    try:
        # 实时读取输出 - 无进度指示器
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            if line:
                line = line.rstrip('\n\r')
                if line.strip():
                    output_lines.append(line.strip())
                    if show_output:
                        print(f"{line.strip()}")
                        sys.stdout.flush()
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_callback(line.strip())
    
    except Exception as e:
        if show_output:
            print(f"读取输出时出错: {e}")
    
    # 获取返回码
    return_code = process.wait()
    
    # 完整输出
    full_output = '\n'.join(output_lines)
    
    if return_code == 0:
        return full_output
    else:
        return f"执行命令时出错 (返回码: {return_code}): {full_output}"

def run_shell_command_with_progress(command: str) -> str:
    """
    执行 shell 命令并显示详细进度信息。
    这是一个便捷方法，专门用于需要详细进度显示的场景。
    """
    def progress_callback(line: str):
        """进度回调函数"""
        # 检测常见的进度指示器
        if any(indicator in line.lower() for indicator in ['downloading', 'installing', 'building', 'compiling']):
            print(f"进度: {line}")
    
    return run_shell_command(command, show_output=True, progress_callback=progress_callback, interactive=True)

def run_shell_command_non_interactive(command: str, show_output: bool = True) -> str:
    """
    执行非交互式 shell 命令。
    用于不需要用户交互的命令，避免等待用户输入。
    """
    return run_shell_command(command, show_output=show_output, interactive=False)