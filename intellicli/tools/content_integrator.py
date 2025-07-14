"""
内容整合工具模块
提供基于LLM的内容整合、处理和分析功能
"""

import os
import json
import yaml
import re
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# 全局模型客户端，将由系统初始化时设置
_model_client = None

# Token 限制配置
MAX_INPUT_TOKENS = 100000  # 保守估计，留出安全边距
OVERLAP_TOKENS = 2000      # 块之间的重叠部分

def set_model_client(model_client):
    """设置全局模型客户端"""
    global _model_client
    _model_client = model_client

def _estimate_tokens(text: str) -> int:
    """估算文本的token数量（粗略估计）"""
    # 粗略估计：中文 1 字符 ≈ 2 tokens，英文 1 字符 ≈ 0.3 tokens
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    other_chars = len(text) - chinese_chars - english_chars
    
    estimated_tokens = chinese_chars * 2 + english_chars * 0.3 + other_chars * 0.5
    return int(estimated_tokens)

def _split_text_into_chunks(text: str, max_tokens: int = MAX_INPUT_TOKENS, overlap: int = OVERLAP_TOKENS) -> List[str]:
    """将长文本分割成多个chunks，保持语义完整性"""
    if _estimate_tokens(text) <= max_tokens:
        return [text]
    
    chunks = []
    
    # 按段落分割
    paragraphs = re.split(r'\n\s*\n', text)
    
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        paragraph_tokens = _estimate_tokens(paragraph)
        
        # 如果单个段落就超过限制，需要进一步分割
        if paragraph_tokens > max_tokens:
            # 如果当前chunk不为空，先保存
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_tokens = 0
            
            # 分割长段落
            sentences = re.split(r'[.!?。！？]\s*', paragraph)
            temp_chunk = ""
            temp_tokens = 0
            
            for sentence in sentences:
                if not sentence.strip():
                    continue
                    
                sentence_tokens = _estimate_tokens(sentence)
                
                if temp_tokens + sentence_tokens > max_tokens:
                    if temp_chunk:
                        chunks.append(temp_chunk.strip())
                        # 保留重叠部分
                        overlap_text = temp_chunk[-overlap:] if len(temp_chunk) > overlap else temp_chunk
                        temp_chunk = overlap_text + sentence
                        temp_tokens = _estimate_tokens(temp_chunk)
                    else:
                        # 如果单个句子太长，强制分割
                        while sentence:
                            chunk_size = min(max_tokens * 2, len(sentence))  # 粗略估计字符数
                            chunk_part = sentence[:chunk_size]
                            chunks.append(chunk_part)
                            sentence = sentence[chunk_size - overlap:]
                        temp_chunk = ""
                        temp_tokens = 0
                else:
                    temp_chunk += sentence + "。"
                    temp_tokens += sentence_tokens
            
            if temp_chunk:
                current_chunk = temp_chunk
                current_tokens = temp_tokens
        else:
            # 检查是否需要开始新的chunk
            if current_tokens + paragraph_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # 保留重叠部分
                    overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = overlap_text + "\n\n" + paragraph
                    current_tokens = _estimate_tokens(current_chunk)
                else:
                    current_chunk = paragraph
                    current_tokens = paragraph_tokens
            else:
                current_chunk += "\n\n" + paragraph
                current_tokens += paragraph_tokens
    
    # 添加最后一个chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def _merge_extraction_results(results: List[str], output_structure: str = "json") -> str:
    """合并多个提取结果"""
    if not results:
        return ""
    
    if len(results) == 1:
        return results[0]
    
    if output_structure.lower() == "json":
        # 尝试合并JSON结果
        merged_data = {}
        for result in results:
            try:
                data = json.loads(result)
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key in merged_data:
                            if isinstance(merged_data[key], list) and isinstance(value, list):
                                merged_data[key].extend(value)
                            elif isinstance(merged_data[key], str) and isinstance(value, str):
                                merged_data[key] += f"\n{value}"
                            else:
                                merged_data[key] = value
                        else:
                            merged_data[key] = value
                elif isinstance(data, list):
                    if "items" not in merged_data:
                        merged_data["items"] = []
                    merged_data["items"].extend(data)
            except:
                # 如果解析失败，作为文本处理
                if "raw_text" not in merged_data:
                    merged_data["raw_text"] = []
                merged_data["raw_text"].append(result)
        
        return json.dumps(merged_data, ensure_ascii=False, indent=2)
    else:
        # 文本格式直接合并
        return "\n\n--- 分块结果分隔符 ---\n\n".join(results)

def integrate_content(
    content: Union[str, List[str], Dict[str, Any]],
    requirement: str,
    output_format: str = "text",
    model_preference: str = "auto",
    max_tokens: int = 2000,
    temperature: float = 0.7
) -> str:
    """
    使用LLM对内容进行整合处理，支持长文本自动分块处理
    
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
        
        # 检查内容长度，如果超过限制则分块处理
        content_tokens = _estimate_tokens(formatted_content)
        
        if content_tokens > MAX_INPUT_TOKENS:
            print(f"⚠️  内容过长 ({content_tokens} tokens)，启用分块处理...")
            
            # 分割内容
            chunks = _split_text_into_chunks(formatted_content)
            print(f"📦 已分割为 {len(chunks)} 个处理块")
            
            # 分别处理每个块
            chunk_results = []
            for i, chunk in enumerate(chunks):
                print(f"🔄 处理块 {i+1}/{len(chunks)}...")
                
                # 为每个块构建提示
                chunk_prompt = _build_integration_prompt(
                    chunk, 
                    requirement + f"\n\n注意：这是第{i+1}个处理块，共{len(chunks)}个块。", 
                    output_format
                )
                
                # 调用LLM处理块
                if _model_client:
                    chunk_result = _model_client.generate(chunk_prompt)
                    chunk_results.append(chunk_result)
                else:
                    return "内容整合失败: 未设置模型客户端"
            
            # 合并结果
            print("🔗 正在合并处理结果...")
            final_result = _merge_extraction_results(chunk_results, output_format)
            return final_result
        else:
            # 内容长度合适，直接处理
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
                return "内容整合失败: 未设置模型客户端"
        
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
    从内容中提取特定信息，支持长文本自动分块处理
    
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
    5. 如果这是分块处理的一部分，请提取该块中的所有相关信息
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