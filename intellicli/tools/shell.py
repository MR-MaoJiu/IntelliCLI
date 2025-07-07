import subprocess

def run_shell_command(command: str) -> str:
    """执行 shell 命令并返回输出。"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"执行命令时出错: {result.stderr}"
    except Exception as e:
        return f"执行命令时出错: {e}"