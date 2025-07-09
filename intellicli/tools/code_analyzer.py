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

# 全局模型客户端变量
_global_model_client = None

def set_model_client(model_client):
    """设置全局模型客户端"""
    global _global_model_client
    _global_model_client = model_client

def get_model_client():
    """获取当前的模型客户端"""
    return _global_model_client

class CodeAnalyzer:
    """代码分析工具类"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.model_client = None
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql'
        }

    def set_model_client(self, model_client):
        """设置代码分析使用的模型客户端"""
        self.model_client = model_client

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

    def analyze_code_with_ai(self, file_path: str, analysis_type: str = "general") -> str:
        """使用AI模型分析代码"""
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法进行AI代码分析"
        
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 获取文件扩展名和语言类型
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext.lower(), 'unknown')
            
            # 构建分析提示
            analysis_prompts = {
                "general": f"""
                请分析以下{language}代码，提供以下信息：
                1. 代码功能和目的
                2. 代码结构和组织
                3. 关键函数和类的说明
                4. 代码质量评估
                5. 潜在的改进建议
                
                文件路径: {file_path}
                代码内容:
                {code_content}
                """,
                "quality": f"""
                请从代码质量角度分析以下{language}代码：
                1. 代码可读性
                2. 性能优化建议
                3. 错误处理
                4. 代码重构建议
                5. 最佳实践遵循情况
                
                文件路径: {file_path}
                代码内容:
                {code_content}
                """,
                "security": f"""
                请从安全角度分析以下{language}代码：
                1. 潜在的安全漏洞
                2. 输入验证问题
                3. 权限控制问题
                4. 数据泄露风险
                5. 安全修复建议
                
                文件路径: {file_path}
                代码内容:
                {code_content}
                """,
                "performance": f"""
                请从性能角度分析以下{language}代码：
                1. 性能瓶颈识别
                2. 算法复杂度分析
                3. 内存使用优化
                4. 并发性能考虑
                5. 性能优化建议
                
                文件路径: {file_path}
                代码内容:
                {code_content}
                """
            }
            
            prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"分析代码时出错: {e}"

    def generate_code_documentation(self, file_path: str) -> str:
        """生成代码文档"""
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法生成代码文档"
        
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext.lower(), 'unknown')
            
            prompt = f"""
            请为以下{language}代码生成详细的文档：
            
            文件路径: {file_path}
            代码内容:
            {code_content}
            
            请生成包含以下内容的文档：
            1. 文件概述和目的
            2. 依赖项和导入说明
            3. 函数和类的详细说明
            4. 参数和返回值说明
            5. 使用示例
            6. 注意事项和限制
            
            请使用Markdown格式，并确保文档清晰易懂。
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"生成代码文档时出错: {e}"

    def suggest_code_improvements(self, file_path: str) -> str:
        """建议代码改进"""
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法提供代码改进建议"
        
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext.lower(), 'unknown')
            
            prompt = f"""
            请为以下{language}代码提供改进建议：
            
            文件路径: {file_path}
            代码内容:
            {code_content}
            
            请提供：
            1. 具体的改进建议
            2. 改进前后的代码对比
            3. 改进理由和好处
            4. 实施难度评估
            5. 优先级建议
            
            请重点关注：
            - 代码可读性和维护性
            - 性能优化
            - 错误处理
            - 代码重构
            - 最佳实践
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"生成代码改进建议时出错: {e}"

    def explain_code_logic(self, file_path: str) -> str:
        """解释代码逻辑"""
        model_client = _global_model_client or self.model_client
        
        if not model_client:
            return "未设置模型客户端，无法解释代码逻辑"
        
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            _, ext = os.path.splitext(file_path)
            language = self.supported_extensions.get(ext.lower(), 'unknown')
            
            prompt = f"""
            请详细解释以下{language}代码的逻辑：
            
            文件路径: {file_path}
            代码内容:
            {code_content}
            
            请提供：
            1. 代码的整体执行流程
            2. 关键算法和数据结构的解释
            3. 各个函数和类的作用
            4. 代码的设计思路
            5. 与其他模块的交互方式
            
            请用通俗易懂的语言解释，适合不同技术水平的读者。
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"解释代码逻辑时出错: {e}"

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

# 增强的代码分析函数
def analyze_code_quality(file_path: str) -> str:
    """分析代码质量"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        # 使用AI分析
        ai_analysis = analyzer.analyze_code_with_ai(file_path, "quality")
        return ai_analysis
    
    # 如果没有模型客户端，使用原有的静态分析
    if not os.path.exists(file_path):
        return f"文件不存在: {file_path}"
    
    try:
        analysis = analyzer.analyze_code_quality(file_path)
        
        result = f"代码质量分析报告: {file_path}\n"
        result += "=" * 50 + "\n\n"
        
        # 基本信息
        result += f"文件大小: {analysis['file_size']} 字节\n"
        result += f"代码行数: {analysis['line_count']} 行\n"
        result += f"空行数: {analysis['blank_lines']} 行\n"
        result += f"注释行数: {analysis['comment_lines']} 行\n"
        result += f"代码密度: {analysis['code_density']:.1%}\n\n"
        
        # 质量指标
        result += "质量指标:\n"
        for metric, value in analysis['quality_metrics'].items():
            result += f"  {metric}: {value}\n"
        
        # 问题列表
        if analysis['issues']:
            result += f"\n发现的问题 ({len(analysis['issues'])} 个):\n"
            for issue in analysis['issues']:
                result += f"  - 行 {issue['line']}: {issue['message']}\n"
        
        # 建议
        if analysis['suggestions']:
            result += f"\n改进建议:\n"
            for suggestion in analysis['suggestions']:
                result += f"  - {suggestion}\n"
        
        return result
        
    except Exception as e:
        return f"分析代码质量时出错: {e}"

def find_security_issues(file_path: str) -> str:
    """查找安全问题"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        # 使用AI分析安全问题
        ai_analysis = analyzer.analyze_code_with_ai(file_path, "security")
        return ai_analysis
    
    # 如果没有模型客户端，使用原有的静态分析
    if not os.path.exists(file_path):
        return f"文件不存在: {file_path}"
    
    try:
        issues = analyzer.find_security_issues(file_path)
        
        if not issues:
            return f"✅ 未发现明显的安全问题: {file_path}"
        
        result = f"🔒 安全问题分析: {file_path}\n"
        result += "=" * 50 + "\n\n"
        result += f"发现 {len(issues)} 个潜在安全问题:\n\n"
        
        for i, issue in enumerate(issues, 1):
            result += f"{i}. {issue['type']}\n"
            result += f"   位置: 行 {issue['line']}\n"
            result += f"   描述: {issue['description']}\n"
            result += f"   风险等级: {issue['risk_level']}\n\n"
        
        return result
        
    except Exception as e:
        return f"查找安全问题时出错: {e}"

def generate_code_documentation(file_path: str) -> str:
    """生成代码文档"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        return analyzer.generate_code_documentation(file_path)
    
    return "未设置模型客户端，无法生成代码文档"

def suggest_code_improvements(file_path: str) -> str:
    """建议代码改进"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        return analyzer.suggest_code_improvements(file_path)
    
    return "未设置模型客户端，无法提供代码改进建议"

def explain_code_logic(file_path: str) -> str:
    """解释代码逻辑"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        return analyzer.explain_code_logic(file_path)
    
    return "未设置模型客户端，无法解释代码逻辑"

def analyze_code_performance(file_path: str) -> str:
    """分析代码性能"""
    analyzer = CodeAnalyzer(os.path.dirname(file_path))
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        return analyzer.analyze_code_with_ai(file_path, "performance")
    
    return "未设置模型客户端，无法分析代码性能"

def review_code_architecture(project_path: str) -> str:
    """审查代码架构"""
    analyzer = CodeAnalyzer(project_path)
    
    # 使用全局模型客户端
    model_client = get_model_client()
    if model_client:
        analyzer.set_model_client(model_client)
        
        try:
            # 获取项目结构
            structure_info = analyzer.analyze_project_structure()
            
            # 分析依赖关系
            dependency_info = analyzer.analyze_python_dependencies()
            
            # 构建架构审查提示
            prompt = f"""
            请审查以下项目的代码架构：
            
            项目路径: {project_path}
            
            项目结构信息:
            {structure_info}
            
            依赖关系信息:
            {dependency_info}
            
            请提供：
            1. 架构模式分析
            2. 模块耦合度评估
            3. 代码组织合理性
            4. 架构优化建议
            5. 技术栈评估
            6. 可维护性分析
            
            请从软件架构师的角度提供专业建议。
            """
            
            return model_client.generate(prompt)
            
        except Exception as e:
            return f"审查代码架构时出错: {e}"
    
    return "未设置模型客户端，无法审查代码架构" 