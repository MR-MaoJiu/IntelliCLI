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

class DocumentManager:
    """文档管理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.doc_extensions = ['.md', '.txt', '.rst', '.adoc', '.html', '.pdf']
        self.code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php']
        
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
        """生成项目README"""
        readme_content = []
        
        # 项目标题
        project_name = os.path.basename(os.path.abspath(self.project_root))
        readme_content.append(f"# {project_name}\n")
        
        # 项目结构
        readme_content.append("## 项目结构\n")
        readme_content.append("```")
        
        # 生成目录树
        for root, dirs, files in os.walk(self.project_root):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            level = root.replace(self.project_root, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root)
            if level == 0:
                readme_content.append(f"{project_name}/")
            else:
                readme_content.append(f"{indent}{folder_name}/")
            
            # 添加文件
            subindent = '  ' * (level + 1)
            for file in files:
                if not file.startswith('.'):
                    readme_content.append(f"{subindent}{file}")
        
        readme_content.append("```\n")
        
        # 文件统计
        readme_content.append("## 文件统计\n")
        
        file_stats = defaultdict(int)
        total_files = 0
        total_lines = 0
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file)
                
                if ext:
                    file_stats[ext.lower()] += 1
                    total_files += 1
                    
                    # 计算行数
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            total_lines += lines
                    except:
                        pass
        
        readme_content.append(f"- 总文件数: {total_files}")
        readme_content.append(f"- 总代码行数: {total_lines}")
        readme_content.append("")
        
        # 按文件类型统计
        readme_content.append("### 文件类型统计\n")
        for ext, count in sorted(file_stats.items()):
            readme_content.append(f"- {ext}: {count} 个文件")
        
        readme_content.append("")
        
        # 查找现有文档
        documents = self.find_documents()
        if documents:
            readme_content.append("## 文档文件\n")
            for doc in documents:
                readme_content.append(f"- [{doc['name']}]({doc['path']})")
        
        return '\n'.join(readme_content)
    
    def extract_api_documentation(self) -> Dict[str, Any]:
        """提取API文档"""
        api_docs = {
            'functions': [],
            'classes': [],
            'constants': []
        }
        
        # 查找Python文件
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取函数和类
                        import ast
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                api_docs['functions'].append({
                                    'name': node.name,
                                    'file': os.path.relpath(file_path, self.project_root),
                                    'line': node.lineno,
                                    'docstring': ast.get_docstring(node) or "无文档",
                                    'args': [arg.arg for arg in node.args.args]
                                })
                            elif isinstance(node, ast.ClassDef):
                                api_docs['classes'].append({
                                    'name': node.name,
                                    'file': os.path.relpath(file_path, self.project_root),
                                    'line': node.lineno,
                                    'docstring': ast.get_docstring(node) or "无文档"
                                })
                    except:
                        pass
        
        return api_docs

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
    """生成项目README"""
    try:
        doc_manager = DocumentManager(project_path)
        readme_content = doc_manager.generate_project_readme()
        
        # 保存到文件
        readme_path = os.path.join(project_path, "README_generated.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        result = f"📝 项目README已生成\n"
        result += f"{'='*50}\n\n"
        result += f"📄 文件路径: {readme_path}\n"
        result += f"📏 内容长度: {len(readme_content)} 字符\n\n"
        result += "📋 README内容预览:\n"
        result += "```markdown\n"
        result += readme_content[:500] + "...\n"
        result += "```\n"
        
        return result
        
    except Exception as e:
        return f"❌ 生成README时出错: {e}"

def extract_api_documentation(project_path: str = ".") -> str:
    """提取API文档"""
    try:
        doc_manager = DocumentManager(project_path)
        api_docs = doc_manager.extract_api_documentation()
        
        result = f"📖 API文档提取\n"
        result += f"{'='*50}\n\n"
        
        # 函数统计
        result += f"🔧 函数: {len(api_docs['functions'])} 个\n"
        result += f"📦 类: {len(api_docs['classes'])} 个\n\n"
        
        # 函数列表
        if api_docs['functions']:
            result += "🔧 函数列表:\n"
            for func in api_docs['functions']:
                result += f"  • {func['name']}({', '.join(func['args'])})\n"
                result += f"    文件: {func['file']}:{func['line']}\n"
                result += f"    说明: {func['docstring'][:100]}...\n\n"
        
        # 类列表
        if api_docs['classes']:
            result += "📦 类列表:\n"
            for cls in api_docs['classes']:
                result += f"  • {cls['name']}\n"
                result += f"    文件: {cls['file']}:{cls['line']}\n"
                result += f"    说明: {cls['docstring'][:100]}...\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ 提取API文档时出错: {e}"

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