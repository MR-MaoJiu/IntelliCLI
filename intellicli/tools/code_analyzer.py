"""
代码分析工具
提供代码架构分析、依赖分析、质量检查等功能
"""

import os
import ast
import json
import re
from typing import Dict, List, Set, Any
from collections import defaultdict
import subprocess

class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.python_files = []
        self.js_files = []
        self.dependencies = defaultdict(set)
        self.functions = []
        self.classes = []
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """分析项目架构"""
        structure = {
            'directories': [],
            'files': {},
            'language_stats': {},
            'total_files': 0,
            'total_lines': 0
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 跳过隐藏目录和常见的忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
            
            rel_root = os.path.relpath(root, self.project_root)
            if rel_root != '.':
                structure['directories'].append(rel_root)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_root)
                
                # 获取文件扩展名
                _, ext = os.path.splitext(file)
                if ext:
                    ext = ext.lower()
                    structure['language_stats'][ext] = structure['language_stats'].get(ext, 0) + 1
                
                # 统计文件信息
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        structure['files'][rel_path] = {
                            'extension': ext,
                            'lines': lines,
                            'size': os.path.getsize(file_path)
                        }
                        structure['total_lines'] += lines
                        structure['total_files'] += 1
                except:
                    pass
        
        return structure
    
    def analyze_python_dependencies(self) -> Dict[str, List[str]]:
        """分析Python依赖关系"""
        dependencies = defaultdict(list)
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.project_root)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        tree = ast.parse(content)
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    dependencies[rel_path].append(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    dependencies[rel_path].append(node.module)
                                    
                    except Exception as e:
                        dependencies[rel_path].append(f"Error parsing: {e}")
        
        return dict(dependencies)
    
    def analyze_code_quality(self, file_path: str) -> Dict[str, Any]:
        """分析代码质量"""
        quality_report = {
            'file': file_path,
            'issues': [],
            'metrics': {},
            'suggestions': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # 基础指标
            quality_report['metrics'] = {
                'lines_of_code': len(lines),
                'empty_lines': sum(1 for line in lines if not line.strip()),
                'comment_lines': sum(1 for line in lines if line.strip().startswith('#')),
                'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            }
            
            # 代码质量检查
            if file_path.endswith('.py'):
                quality_report.update(self._analyze_python_quality(content, lines))
            elif file_path.endswith('.js'):
                quality_report.update(self._analyze_js_quality(content, lines))
                
        except Exception as e:
            quality_report['issues'].append(f"Error analyzing file: {e}")
        
        return quality_report
    
    def _analyze_python_quality(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """分析Python代码质量"""
        issues = []
        suggestions = []
        
        try:
            tree = ast.parse(content)
            
            # 检查函数和类
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 检查函数长度
                    func_lines = node.end_lineno - node.lineno + 1
                    if func_lines > 50:
                        issues.append(f"Function '{node.name}' is too long ({func_lines} lines)")
                    
                    # 检查是否有文档字符串
                    if not ast.get_docstring(node):
                        suggestions.append(f"Add docstring to function '{node.name}'")
                        
                elif isinstance(node, ast.ClassDef):
                    # 检查类文档字符串
                    if not ast.get_docstring(node):
                        suggestions.append(f"Add docstring to class '{node.name}'")
            
            # 检查代码风格
            for i, line in enumerate(lines, 1):
                if len(line) > 100:
                    issues.append(f"Line {i} is too long ({len(line)} characters)")
                    
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
        except Exception as e:
            issues.append(f"Analysis error: {e}")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _analyze_js_quality(self, content: str, lines: List[str]) -> Dict[str, Any]:
        """分析JavaScript代码质量"""
        issues = []
        suggestions = []
        
        # 基础JavaScript质量检查
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"Line {i} is too long ({len(line)} characters)")
            
            # 检查常见问题
            if '==' in line and '===' not in line:
                suggestions.append(f"Line {i}: Consider using '===' instead of '=='")
            
            if 'var ' in line:
                suggestions.append(f"Line {i}: Consider using 'let' or 'const' instead of 'var'")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def find_security_issues(self, file_path: str) -> List[Dict[str, str]]:
        """查找安全问题"""
        security_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 常见安全问题模式
            security_patterns = [
                (r'eval\s*\(', 'Potential code injection vulnerability with eval()'),
                (r'exec\s*\(', 'Potential code injection vulnerability with exec()'),
                (r'os\.system\s*\(', 'Potential command injection vulnerability'),
                (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'Command injection risk with shell=True'),
                (r'password\s*=\s*["\'][^"\']*["\']', 'Hardcoded password detected'),
                (r'api_key\s*=\s*["\'][^"\']*["\']', 'Hardcoded API key detected'),
                (r'secret\s*=\s*["\'][^"\']*["\']', 'Hardcoded secret detected'),
            ]
            
            for pattern, description in security_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    security_issues.append({
                        'file': file_path,
                        'line': line_no,
                        'issue': description,
                        'code': match.group(0)
                    })
                    
        except Exception as e:
            security_issues.append({
                'file': file_path,
                'line': 0,
                'issue': f'Error analyzing file: {e}',
                'code': ''
            })
        
        return security_issues

def analyze_project_structure(project_path: str) -> str:
    """分析项目结构"""
    try:
        analyzer = CodeAnalyzer(project_path)
        structure = analyzer.analyze_project_structure()
        
        result = f"📊 项目结构分析报告\n"
        result += f"{'='*50}\n\n"
        result += f"📁 总文件数: {structure['total_files']}\n"
        result += f"📄 总代码行数: {structure['total_lines']}\n"
        result += f"📂 目录数: {len(structure['directories'])}\n\n"
        
        result += f"🔤 语言统计:\n"
        for ext, count in sorted(structure['language_stats'].items()):
            result += f"  {ext}: {count} 个文件\n"
        
        result += f"\n📂 目录结构:\n"
        for directory in sorted(structure['directories']):
            result += f"  {directory}/\n"
        
        return result
        
    except Exception as e:
        return f"❌ 分析项目结构时出错: {e}"

def analyze_python_dependencies(project_path: str) -> str:
    """分析Python依赖关系"""
    try:
        analyzer = CodeAnalyzer(project_path)
        dependencies = analyzer.analyze_python_dependencies()
        
        result = f"🔗 Python依赖关系分析\n"
        result += f"{'='*50}\n\n"
        
        for file_path, deps in dependencies.items():
            result += f"📄 {file_path}:\n"
            for dep in deps:
                result += f"  └── {dep}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 分析依赖关系时出错: {e}"

def analyze_code_quality(file_path: str) -> str:
    """分析代码质量"""
    try:
        analyzer = CodeAnalyzer(os.path.dirname(file_path))
        quality_report = analyzer.analyze_code_quality(file_path)
        
        result = f"📊 代码质量分析报告\n"
        result += f"{'='*50}\n\n"
        result += f"📄 文件: {quality_report['file']}\n\n"
        
        # 指标
        metrics = quality_report['metrics']
        result += f"📏 基础指标:\n"
        result += f"  • 代码行数: {metrics['lines_of_code']}\n"
        result += f"  • 空行数: {metrics['empty_lines']}\n"
        result += f"  • 注释行数: {metrics['comment_lines']}\n"
        result += f"  • 平均行长度: {metrics['avg_line_length']:.1f}\n\n"
        
        # 问题
        if quality_report['issues']:
            result += f"❌ 发现问题:\n"
            for issue in quality_report['issues']:
                result += f"  • {issue}\n"
            result += "\n"
        
        # 建议
        if quality_report['suggestions']:
            result += f"💡 改进建议:\n"
            for suggestion in quality_report['suggestions']:
                result += f"  • {suggestion}\n"
        
        return result
        
    except Exception as e:
        return f"❌ 分析代码质量时出错: {e}"

def find_security_issues(file_path: str) -> str:
    """查找安全问题"""
    try:
        analyzer = CodeAnalyzer(os.path.dirname(file_path))
        security_issues = analyzer.find_security_issues(file_path)
        
        result = f"🔒 安全问题分析报告\n"
        result += f"{'='*50}\n\n"
        result += f"📄 文件: {file_path}\n\n"
        
        if security_issues:
            result += f"⚠️  发现 {len(security_issues)} 个潜在安全问题:\n\n"
            for issue in security_issues:
                result += f"  🚨 第 {issue['line']} 行:\n"
                result += f"     问题: {issue['issue']}\n"
                result += f"     代码: {issue['code']}\n\n"
        else:
            result += f"✅ 未发现明显的安全问题\n"
        
        return result
        
    except Exception as e:
        return f"❌ 分析安全问题时出错: {e}" 