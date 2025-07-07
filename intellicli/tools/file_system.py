import os

def read_file(path: str) -> str:
    """读取文件的内容。"""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"读取文件时出错: {e}"

def write_file(path: str, content: str) -> str:
    """将内容写入文件。"""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"成功写入文件: {path}"
    except Exception as e:
        return f"写入文件时出错: {e}"

def list_directory(path: str) -> str:
    """列出目录的内容。"""
    try:
        return "\n".join(os.listdir(path))
    except Exception as e:
        return f"列出目录时出错: {e}"