import os
import ast
from typing import Dict, List

def find_and_extract_first_function(file_paths: List[str]) -> Dict[str, str]:
    """
    从提供的 Python 文件路径列表中提取每个文件的第一个函数定义。

    Args:
        file_paths (List[str]): Python 文件的路径列表。

    Returns:
        Dict[str, str]: 一个字典，键是 Python 文件的路径，值是该文件中第一个函数定义的代码字符串。
                        如果文件没有函数定义，则该文件不会包含在字典中。
    """
    results = {}
    
    # 处理传入的文件路径列表
    for file_path in file_paths:
        # 确保文件路径存在且是 Python 文件
        if not os.path.exists(file_path):
            print(f"警告: 文件 {file_path} 不存在")
            continue
            
        if not file_path.endswith('.py'):
            print(f"警告: 文件 {file_path} 不是 Python 文件")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            first_function_def = None
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    first_function_def = ast.get_source_segment(content, node)
                    break # 找到第一个函数定义后即停止
            
            if first_function_def:
                results[file_path] = first_function_def
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
    
    return results