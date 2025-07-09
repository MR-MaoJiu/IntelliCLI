"""
文档管理工具
提供文档生成、搜索、转换等功能
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
from collections import defaultdict
import subprocess

# 全局模型客户端变量
_global_model_client = None

def set_model_client(model_client):
    """设置全局模型客户端"""
    global _global_model_client
    _global_model_client = model_client

def get_model_client():
    """获取当前的模型客户端"""
    return _global_model_client

class DocumentManager:
    """文档管理和生成工具"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.model_client = None
        self.doc_extensions = ['.md', '.txt', '.rst', '.doc', '.docx', '.pdf', '.html']
        self.code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php']
        
    def set_model_client(self, model_client):
        """设置文档管理使用的模型客户端"""
        self.model_client = model_client

    def find_documents(self) -> List[Dict[str, Any]]:
        """查找所有文档文件"""
        documents = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 跳过常见的忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env', 'build', 'dist']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # 检查是否是文档文件
                _, ext = os.path.splitext(file)
                if ext.lower() in self.doc_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        documents.append({
                            'path': rel_path,
                            'name': file,
                            'extension': ext.lower(),
                            'size': os.path.getsize(file_path),
                            'lines': len(content.split('\n')),
                            'content': content
                        })
                    except Exception as e:
                        documents.append({
                            'path': rel_path,
                            'name': file,
                            'extension': ext.lower(),
                            'size': os.path.getsize(file_path),
                            'error': str(e)
                        })
        
        return documents
    
    def search_in_documents(self, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """在文档中搜索内容"""
        documents = self.find_documents()
        results = []
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for doc in documents:
            if 'content' not in doc:
                continue
                
            content = doc['content']
            matches = []
            
            # 搜索匹配项
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(query, line, flags):
                    matches.append({
                        'line_number': i,
                        'line_content': line.strip(),
                        'match': re.search(query, line, flags).group(0)
                    })
            
            if matches:
                results.append({
                    'document': doc['path'],
                    'matches': matches,
                    'match_count': len(matches)
                })
        
        return results
    
    def generate_project_readme(self) -> str:
        """生成项目README文档"""
        # 使用全局模型客户端或实例模型客户端
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法生成README文档"
        
        try:
            # 获取项目结构信息
            project_structure = self.analyze_project_structure()
            
            # 查找现有文档
            existing_docs = self.find_documents()
            
            # 构建生成提示
            prompt = f"""
            请根据以下项目信息生成一个专业的README.md文档：
            
            项目结构：
            {project_structure}
            
            现有文档：
            {existing_docs}
            
            请生成包含以下部分的README：
            1. 项目标题和简介
            2. 功能特性
            3. 安装说明
            4. 使用方法
            5. 项目结构说明
            6. 贡献指南
            7. 许可证信息
            
            请使用Markdown格式，内容要详细且专业。
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"生成README文档时出错: {e}"
    
    def extract_api_documentation(self) -> Dict[str, Any]:
        """提取API文档"""
        # 使用全局模型客户端或实例模型客户端
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return {"error": "未设置模型客户端，无法提取API文档"}
        
        try:
            # 查找Python文件
            python_files = []
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            api_docs = {}
            
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用模型分析代码并提取API文档
                    prompt = f"""
                    请分析以下Python代码并提取API文档信息：
                    
                    文件路径：{file_path}
                    
                    代码内容：
                    {content}
                    
                    请提取：
                    1. 所有公共函数和类
                    2. 函数/类的用途说明
                    3. 参数说明
                    4. 返回值说明
                    5. 使用示例
                    
                    请以结构化的方式组织信息。
                    """
                    
                    api_info = model_client.generate(prompt)
                    api_docs[file_path] = api_info
                    
                except Exception as e:
                    api_docs[file_path] = f"分析文件时出错: {e}"
            
            return api_docs
            
        except Exception as e:
            return {"error": f"提取API文档时出错: {e}"}

    def analyze_project_structure(self) -> str:
        """分析项目结构"""
        try:
            structure = []
            
            # 遍历项目目录
            for root, dirs, files in os.walk(self.project_root):
                # 跳过隐藏目录和常见的忽略目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                level = root.replace(self.project_root, '').count(os.sep)
                indent = '  ' * level
                structure.append(f"{indent}{os.path.basename(root)}/")
                
                # 添加文件
                subindent = '  ' * (level + 1)
                for file in files:
                    if not file.startswith('.'):
                        structure.append(f"{subindent}{file}")
            
            return '\n'.join(structure)
            
        except Exception as e:
            return f"分析项目结构时出错: {e}"

    def generate_technical_documentation(self, doc_type: str, content: str) -> str:
        """生成技术文档"""
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法生成技术文档"
        
        try:
            prompt = f"""
            请根据以下信息生成{doc_type}技术文档：
            
            内容：
            {content}
            
            请生成专业的技术文档，包含：
            1. 清晰的标题和结构
            2. 详细的说明
            3. 代码示例（如适用）
            4. 使用指南
            5. 注意事项
            
            请使用Markdown格式。
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"生成技术文档时出错: {e}"

def find_all_documents(project_path: str = ".") -> str:
    """查找所有文档文件"""
    try:
        doc_manager = DocumentManager(project_path)
        documents = doc_manager.find_documents()
        
        result = f"📚 文档文件列表\n"
        result += f"{'='*50}\n\n"
        
        if not documents:
            result += "没有找到文档文件\n"
            return result
        
        # 按类型分组
        docs_by_type = defaultdict(list)
        for doc in documents:
            docs_by_type[doc['extension']].append(doc)
        
        result += f"📊 总计: {len(documents)} 个文档文件\n\n"
        
        for ext, docs in docs_by_type.items():
            result += f"📄 {ext.upper()} 文件 ({len(docs)} 个):\n"
            for doc in docs:
                size_kb = doc['size'] / 1024
                if 'lines' in doc:
                    result += f"  • {doc['path']} ({doc['lines']} 行, {size_kb:.1f}KB)\n"
                else:
                    result += f"  • {doc['path']} ({size_kb:.1f}KB)\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 查找文档时出错: {e}"

def search_in_documents(query: str, project_path: str = ".", case_sensitive: bool = False) -> str:
    """在文档中搜索内容"""
    try:
        doc_manager = DocumentManager(project_path)
        results = doc_manager.search_in_documents(query, case_sensitive)
        
        result = f"🔍 文档搜索结果\n"
        result += f"{'='*50}\n\n"
        result += f"🔍 搜索关键词: {query}\n"
        result += f"📁 搜索范围: {project_path}\n\n"
        
        if not results:
            result += "没有找到匹配的内容\n"
            return result
        
        total_matches = sum(r['match_count'] for r in results)
        result += f"📊 找到 {total_matches} 个匹配项，分布在 {len(results)} 个文档中\n\n"
        
        for doc_result in results:
            result += f"📄 {doc_result['document']} ({doc_result['match_count']} 个匹配)\n"
            for match in doc_result['matches'][:5]:  # 限制显示前5个匹配
                result += f"  第 {match['line_number']} 行: {match['line_content']}\n"
            
            if doc_result['match_count'] > 5:
                result += f"  ... 还有 {doc_result['match_count'] - 5} 个匹配\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 搜索文档时出错: {e}"

def generate_project_readme(project_path: str = ".") -> str:
    """生成项目README文档"""
    manager = DocumentManager(project_path)
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        manager.set_model_client(model_client)
    
    return manager.generate_project_readme()

def extract_api_documentation(project_path: str = ".") -> str:
    """提取API文档"""
    manager = DocumentManager(project_path)
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        manager.set_model_client(model_client)
    
    result = manager.extract_api_documentation()
    
    if "error" in result:
        return result["error"]
    
    # 格式化输出
    formatted_result = "API文档提取结果:\n\n"
    for file_path, api_info in result.items():
        formatted_result += f"文件: {file_path}\n"
        formatted_result += f"API信息:\n{api_info}\n\n"
        formatted_result += "=" * 50 + "\n\n"
    
    return formatted_result

def generate_technical_doc(doc_type: str, content: str, project_path: str = ".") -> str:
    """生成技术文档"""
    manager = DocumentManager(project_path)
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        manager.set_model_client(model_client)
    
    return manager.generate_technical_documentation(doc_type, content)

def analyze_project_architecture(project_path: str = ".") -> str:
    """分析项目架构"""
    manager = DocumentManager(project_path)
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        manager.set_model_client(model_client)
    
    if not model_client:
        return "未设置模型客户端，无法分析项目架构"
    
    try:
        # 获取项目结构
        structure = manager.analyze_project_structure()
        
        # 查找配置文件
        config_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file in ['package.json', 'requirements.txt', 'setup.py', 'Dockerfile', 'docker-compose.yml', 'config.yaml']:
                    config_files.append(os.path.join(root, file))
        
        config_content = ""
        for config_file in config_files:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    config_content += f"\n{config_file}:\n{content}\n"
            except:
                pass
        
        # 使用模型分析架构
        prompt = f"""
        请分析以下项目的架构和技术栈：
        
        项目结构：
        {structure}
        
        配置文件内容：
        {config_content}
        
        请提供：
        1. 项目类型和主要技术栈
        2. 架构模式分析
        3. 模块依赖关系
        4. 部署方式
        5. 潜在的改进建议
        
        请详细分析并提供专业的技术见解。
        """
        
        return model_client.generate(prompt)
        
    except Exception as e:
        return f"分析项目架构时出错: {e}"

def search_code_patterns(pattern: str, project_path: str = ".") -> str:
    """搜索代码模式"""
    try:
        results = []
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                # 只搜索代码文件
                if ext.lower() in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        matches = []
                        for i, line in enumerate(content.split('\n'), 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                matches.append({
                                    'line_number': i,
                                    'line_content': line.strip()
                                })
                        
                        if matches:
                            results.append({
                                'file': os.path.relpath(file_path, project_path),
                                'matches': matches,
                                'match_count': len(matches)
                            })
                    except:
                        pass
        
        result = f"🔍 代码模式搜索\n"
        result += f"{'='*50}\n\n"
        result += f"🔍 搜索模式: {pattern}\n"
        result += f"📁 搜索范围: {project_path}\n\n"
        
        if not results:
            result += "没有找到匹配的代码模式\n"
            return result
        
        total_matches = sum(r['match_count'] for r in results)
        result += f"📊 找到 {total_matches} 个匹配项，分布在 {len(results)} 个文件中\n\n"
        
        for file_result in results:
            result += f"📄 {file_result['file']} ({file_result['match_count']} 个匹配)\n"
            for match in file_result['matches'][:3]:  # 限制显示前3个匹配
                result += f"  第 {match['line_number']} 行: {match['line_content']}\n"
            
            if file_result['match_count'] > 3:
                result += f"  ... 还有 {file_result['match_count'] - 3} 个匹配\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 搜索代码模式时出错: {e}" 