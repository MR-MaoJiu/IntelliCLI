"""
内容整合工具模块
提供基于LLM的内容整合、处理和分析功能
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# 全局模型客户端，将由系统初始化时设置
_model_client = None

def set_model_client(model_client):
    """设置全局模型客户端"""
    global _model_client
    _model_client = model_client

def integrate_content(
    content: Union[str, List[str], Dict[str, Any]],
    requirement: str,
    output_format: str = "text",
    model_preference: str = "auto",
    max_tokens: int = 2000,
    temperature: float = 0.7
) -> str:
    """
    使用LLM对内容进行整合处理
    
    Args:
        content: 要整合的内容，可以是字符串、字符串列表或字典
        requirement: 整合要求和指令
        output_format: 输出格式 ("text", "json", "yaml", "markdown", "html")
        model_preference: 模型偏好 ("auto", "code", "reasoning", "general")
        max_tokens: 最大生成token数
        temperature: 生成温度
    
    Returns:
        整合后的内容字符串
    """
    try:
        # 准备输入内容
        formatted_content = _format_input_content(content)
        
        # 构建整合提示
        integration_prompt = _build_integration_prompt(
            formatted_content, 
            requirement, 
            output_format
        )
        
        # 调用LLM进行整合
        if _model_client:
            result = _model_client.generate(integration_prompt)
            return result
        else:
            return f"内容整合失败: {str(e)}"
        
    except Exception as e:
        return f"内容整合失败: {str(e)}"

def integrate_files(
    file_paths: List[str],
    requirement: str,
    output_format: str = "text",
    include_metadata: bool = True
) -> str:
    """
    整合多个文件的内容
    
    Args:
        file_paths: 文件路径列表
        requirement: 整合要求
        output_format: 输出格式
        include_metadata: 是否包含文件元数据
    
    Returns:
        整合后的内容字符串
    """
    try:
        # 读取所有文件内容
        files_content = []
        for file_path in file_paths:
            file_info = _read_file_content(file_path, include_metadata)
            if file_info:
                files_content.append(file_info)
        
        if not files_content:
            return "错误: 没有成功读取任何文件"
        
        # 使用integrate_content处理
        return integrate_content(
            files_content,
            requirement,
            output_format
        )
        
    except Exception as e:
        return f"文件整合失败: {str(e)}"

def summarize_content(
    content: Union[str, List[str]],
    summary_type: str = "brief",
    key_points: int = 5,
    language: str = "zh"
) -> str:
    """
    对内容进行摘要处理
    
    Args:
        content: 要摘要的内容
        summary_type: 摘要类型 ("brief", "detailed", "bullet_points", "key_insights")
        key_points: 关键点数量
        language: 输出语言
    
    Returns:
        摘要结果字符串
    """
    summary_requirements = {
        "brief": f"请对以下内容进行简洁摘要，用{language}输出，控制在200字以内",
        "detailed": f"请对以下内容进行详细摘要，用{language}输出，包含主要观点和细节",
        "bullet_points": f"请将以下内容总结为{key_points}个关键要点，用{language}输出，使用项目符号格式",
        "key_insights": f"请提取以下内容的{key_points}个核心洞察，用{language}输出，重点关注重要发现和结论"
    }
    
    requirement = summary_requirements.get(summary_type, summary_requirements["brief"])
    
    return integrate_content(
        content,
        requirement,
        output_format="markdown"
    )

def extract_information(
    content: Union[str, List[str]],
    extraction_targets: List[str],
    output_structure: str = "json"
) -> str:
    """
    从内容中提取特定信息
    
    Args:
        content: 源内容
        extraction_targets: 要提取的信息类型列表
        output_structure: 输出结构格式
    
    Returns:
        提取结果字符串
    """
    targets_str = "、".join(extraction_targets)
    requirement = f"""
    请从以下内容中提取以下信息：{targets_str}
    
    要求：
    1. 准确提取所需信息
    2. 如果某项信息不存在，标记为"未找到"
    3. 保持信息的原始准确性
    4. 按照指定的结构格式输出
    """
    
    return integrate_content(
        content,
        requirement,
        output_format=output_structure
    )

def transform_format(
    content: str,
    source_format: str,
    target_format: str,
    preserve_structure: bool = True
) -> str:
    """
    转换内容格式
    
    Args:
        content: 源内容
        source_format: 源格式
        target_format: 目标格式
        preserve_structure: 是否保持结构
    
    Returns:
        转换后的内容字符串
    """
    requirement = f"""
    请将以下{source_format}格式的内容转换为{target_format}格式：
    
    要求：
    1. {'保持原有结构和层次' if preserve_structure else '可以优化结构'}
    2. 确保内容完整性
    3. 适应目标格式的特点
    4. 保持语义一致性
    """
    
    return integrate_content(
        content,
        requirement,
        output_format=target_format
    )

def _format_input_content(content: Union[str, List[str], Dict[str, Any]]) -> str:
    """格式化输入内容"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if all(isinstance(item, str) for item in content):
            return "\n\n".join(f"内容 {i+1}:\n{item}" for i, item in enumerate(content))
        else:
            return "\n\n".join(f"项目 {i+1}:\n{json.dumps(item, ensure_ascii=False, indent=2)}" for i, item in enumerate(content))
    elif isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False, indent=2)
    else:
        return str(content)

def _build_integration_prompt(content: str, requirement: str, output_format: str) -> str:
    """构建整合提示"""
    format_instructions = {
        "text": "以纯文本格式输出",
        "json": "以JSON格式输出，确保格式正确",
        "yaml": "以YAML格式输出，注意缩进",
        "markdown": "以Markdown格式输出，使用适当的标题和格式",
        "html": "以HTML格式输出，使用语义化标签"
    }
    
    format_instruction = format_instructions.get(output_format, "以文本格式输出")
    
    prompt = f"""
作为一个专业的内容整合助手，请根据以下要求对内容进行整合处理：

整合要求：
{requirement}

输出格式要求：
{format_instruction}

待整合内容：
{content}

请严格按照要求进行整合处理，确保输出结果准确、完整、格式正确。
"""
    
    return prompt


def _read_file_content(file_path: str, include_metadata: bool = True) -> Optional[Dict[str, Any]]:
    """读取文件内容"""
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        # 读取文件内容
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_info = {
            "file_path": str(path),
            "content": content
        }
        
        if include_metadata:
            file_info.update({
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "file_extension": path.suffix,
                "modification_time": path.stat().st_mtime
            })
        
        return file_info
        
    except Exception as e:
        return {
            "file_path": file_path,
            "content": f"读取文件失败: {str(e)}",
            "error": True
        }

# 便捷函数
def quick_summary(content: str, max_length: int = 200) -> str:
    """快速摘要"""
    result = summarize_content(content, "brief")
    if len(result) > max_length:
        return result[:max_length] + "..."
    return result

def quick_extract(content: str, target: str) -> str:
    """快速提取"""
    return extract_information(content, [target])

def quick_transform(content: str, target_format: str) -> str:
    """快速格式转换"""
    return transform_format(content, "text", target_format) 