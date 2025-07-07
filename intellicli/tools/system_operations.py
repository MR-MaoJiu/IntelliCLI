import subprocess
import os
import platform
import webbrowser

def open_file(file_path: str) -> str:
    """
    使用系统默认应用程序打开文件。
    
    Args:
        file_path (str): 要打开的文件路径
        
    Returns:
        str: 操作结果信息
    """
    try:
        if not os.path.exists(file_path):
            return f"错误: 文件 {file_path} 不存在"
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Windows":  # Windows
            os.startfile(file_path)
        elif system == "Linux":  # Linux
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            return f"错误: 不支持的操作系统 {system}"
        
        return f"成功打开文件: {file_path}"
    except subprocess.CalledProcessError as e:
        return f"打开文件时出错: {e}"
    except Exception as e:
        return f"打开文件时出错: {e}"

def open_url(url: str) -> str:
    """
    使用默认浏览器打开URL。
    
    Args:
        url (str): 要打开的URL
        
    Returns:
        str: 操作结果信息
    """
    try:
        webbrowser.open(url)
        return f"成功在浏览器中打开: {url}"
    except Exception as e:
        return f"打开URL时出错: {e}"

def start_http_server(directory: str, port: int = 8000) -> str:
    """
    在指定目录启动简单的HTTP服务器。
    
    Args:
        directory (str): 服务器根目录
        port (int): 端口号，默认8000
        
    Returns:
        str: 操作结果信息
    """
    try:
        if not os.path.exists(directory):
            return f"错误: 目录 {directory} 不存在"
        
        # 切换到目标目录
        original_dir = os.getcwd()
        os.chdir(directory)
        
        # 启动HTTP服务器（在后台运行）
        cmd = ["python3", "-m", "http.server", str(port)]
        
        # 检查端口是否可用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            return f"错误: 端口 {port} 已被占用"
        
        # 启动服务器
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 恢复原目录
        os.chdir(original_dir)
        
        # 等待一小段时间确保服务器启动
        import time
        time.sleep(1)
        
        # 在浏览器中打开
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        
        return f"HTTP服务器已启动在端口 {port}，并在浏览器中打开 {url}。进程ID: {process.pid}"
        
    except Exception as e:
        # 确保恢复原目录
        try:
            os.chdir(original_dir)
        except:
            pass
        return f"启动HTTP服务器时出错: {e}"

def show_current_directory() -> str:
    """
    显示当前工作目录。
    
    Returns:
        str: 当前工作目录路径
    """
    try:
        current_dir = os.getcwd()
        return f"当前工作目录: {current_dir}"
    except Exception as e:
        return f"获取当前目录时出错: {e}"

def check_file_exists(file_path: str) -> str:
    """
    检查文件或目录是否存在。
    
    Args:
        file_path (str): 要检查的文件或目录路径
        
    Returns:
        str: 检查结果
    """
    try:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                return f"文件存在: {file_path} (大小: {size} 字节)"
            elif os.path.isdir(file_path):
                files_count = len(os.listdir(file_path))
                return f"目录存在: {file_path} (包含 {files_count} 个项目)"
            else:
                return f"路径存在: {file_path} (特殊文件类型)"
        else:
            return f"路径不存在: {file_path}"
    except Exception as e:
        return f"检查文件时出错: {e}" 