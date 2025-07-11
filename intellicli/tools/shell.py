import subprocess
import threading
import time
import sys
import os
import json
from pathlib import Path
from typing import Optional, Callable, Set

# 用于缓存已知需要直接执行的命令前缀
_direct_execution_cache: Set[str] = set()
_cache_file = Path.home() / '.intellicli_execution_cache.json'

def _load_execution_cache():
    """加载执行模式缓存"""
    global _direct_execution_cache
    try:
        if _cache_file.exists():
            with open(_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _direct_execution_cache = set(data.get('direct_commands', []))
    except Exception:
        _direct_execution_cache = set()

def _save_execution_cache():
    """保存执行模式缓存"""
    try:
        with open(_cache_file, 'w', encoding='utf-8') as f:
            json.dump({'direct_commands': list(_direct_execution_cache)}, f)
    except Exception:
        pass

def _add_to_direct_cache(command: str):
    """将命令前缀添加到直接执行缓存"""
    # 提取命令的前两个词作为模式
    words = command.split()
    if len(words) >= 2:
        pattern = ' '.join(words[:2]).lower()
        _direct_execution_cache.add(pattern)
        _save_execution_cache()

def _should_execute_directly(command: str) -> bool:
    """判断是否需要直接执行（基于缓存学习）"""
    if not _direct_execution_cache:
        _load_execution_cache()
    
    command_lower = command.lower()
    # 检查缓存中的模式
    for pattern in _direct_execution_cache:
        if pattern in command_lower:
            return True
    
    # 启发式检测：检测明显的脚手架工具
    heuristic_indicators = [
        'create-',  # create-vue, create-react-app等
        'init',     # npm init, yarn init等
        'new',      # vue create, ng new等
        'setup'     # 各种setup命令
    ]
    
    return any(indicator in command_lower for indicator in heuristic_indicators)

def run_shell_command(command: str, 
                     show_output: bool = True, 
                     progress_callback: Optional[Callable] = None,
                     timeout: Optional[int] = None,
                     interactive: bool = True) -> str:
    """
    执行 shell 命令并返回输出，智能选择执行模式。
    
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
        # 如果缓存显示需要直接执行，或者启发式检测到
        if _should_execute_directly(command):
            return _handle_direct_execution(command, show_output)
        
        if interactive and hasattr(os, 'openpty'):
            # 尝试透明pty模式，如果失败会自动回退
            result = _handle_interactive_command_with_fallback(command, show_output, progress_callback)
            return result
        else:
            # 非交互模式或Windows系统
            return _handle_non_interactive_command_simple(command, show_output, progress_callback)
            
    except Exception as e:
        return f"执行命令时出错: {e}"

def _detect_output_problems(output_data: bytes, start_time: float) -> bool:
    """检测输出是否有问题，需要回退到直接模式"""
    try:
        # 检测1：如果输出包含大量单字符行（表明格式有问题）
        if output_data:
            text = output_data.decode('utf-8', errors='ignore')
            lines = text.split('\n')
            if len(lines) > 10:
                single_char_lines = sum(1 for line in lines if len(line.strip()) == 1)
                if single_char_lines > len(lines) * 0.5:  # 超过50%是单字符行
                    return True
        
        # 检测2：如果命令运行超过3秒但没有有意义的输出
        if time.time() - start_time > 3 and len(output_data) < 10:
            return True
        
        # 检测3：检测典型的交互式提示符模式
        if output_data:
            text = output_data.decode('utf-8', errors='ignore').lower()
            problematic_patterns = [
                '? project name',
                '? package name', 
                '? select a framework',
                '? add typescript',
                'create a new project'
            ]
            if any(pattern in text for pattern in problematic_patterns):
                return True
                
        return False
    except Exception:
        return False

def _handle_interactive_command_with_fallback(command: str, show_output: bool, progress_callback: Optional[Callable]) -> str:
    """智能执行交互式命令，支持自动回退到直接模式"""
    import pty
    import select
    import tty
    import termios
    
    output_buffer = []
    start_time = time.time()
    problem_detected = False
    
    # 创建伪终端
    master, slave = pty.openpty()
    
    try:
        # 启动进程
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            preexec_fn=os.setsid,
            close_fds=True
        )
        
        os.close(slave)
        
        # 保存原始终端设置
        old_tty = None
        try:
            old_tty = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        except:
            pass
        
        # 监控前几秒的输出，检测是否需要回退
        monitoring_time = 5.0  # 监控前5秒
        
        try:
            while True:
                if process.poll() is not None:
                    # 进程结束，读取剩余输出
                    try:
                        while True:
                            data = os.read(master, 1024)
                            if not data:
                                break
                            if show_output and not problem_detected:
                                sys.stdout.buffer.write(data)
                                sys.stdout.buffer.flush()
                            output_buffer.append(data)
                    except OSError:
                        pass
                    break
                
                # 在监控期间检测问题
                current_time = time.time()
                if current_time - start_time < monitoring_time and not problem_detected:
                    all_output = b''.join(output_buffer)
                    if _detect_output_problems(all_output, start_time):
                        problem_detected = True
                        # 终止当前进程
                        try:
                            os.killpg(os.getpgid(process.pid), 15)  # SIGTERM
                            process.wait(timeout=2)
                        except:
                            try:
                                process.kill()
                            except:
                                pass
                        
                        # 学习这个命令需要直接执行
                        _add_to_direct_cache(command)
                        
                        if show_output:
                            print(f"\n🔄 检测到输出格式问题，切换到直接执行模式...")
                        
                        # 回退到直接执行
                        return _handle_direct_execution(command, show_output)
                
                ready, _, _ = select.select([master, sys.stdin], [], [], 0.01)
                
                if master in ready:
                    try:
                        data = os.read(master, 1024)
                        if data:
                            if show_output and not problem_detected:
                                sys.stdout.buffer.write(data)
                                sys.stdout.buffer.flush()
                            output_buffer.append(data)
                    except OSError:
                        break
                
                if sys.stdin in ready:
                    try:
                        char = sys.stdin.read(1)
                        if char:
                            os.write(master, char.encode('utf-8'))
                    except OSError:
                        break
        
        except KeyboardInterrupt:
            try:
                os.killpg(os.getpgid(process.pid), 2)
            except:
                process.terminate()
        
        finally:
            if old_tty:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
                except:
                    pass
        
        return_code = process.wait()
        
    finally:
        try:
            os.close(master)
        except:
            pass
    
    # 如果没有检测到问题，返回正常结果
    if not problem_detected:
        try:
            result = b''.join(output_buffer).decode('utf-8', errors='ignore')
            return result if result else "命令执行完成"
        except:
            return "命令执行完成"
    
    return "命令通过直接模式执行完成"

def _handle_direct_execution(command: str, show_output: bool) -> str:
    """直接在用户终端执行复杂交互式命令"""
    if show_output:
        print(f"🎯 使用直接执行模式")
        print(f"📝 命令: {command}")
        print(f"🔄 开始执行...")
        print("-" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            check=False
        )
        
        if show_output:
            print("-" * 50)
            if result.returncode == 0:
                print("✅ 命令执行完成")
            else:
                print(f"⚠️ 命令执行完成，返回码: {result.returncode}")
        
        if result.returncode == 0:
            return "命令执行成功（直接模式）"
        else:
            return f"命令执行完成，返回码: {result.returncode}（直接模式）"
            
    except Exception as e:
        error_msg = f"执行命令时出错: {e}"
        if show_output:
            print(f"❌ {error_msg}")
        return error_msg

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