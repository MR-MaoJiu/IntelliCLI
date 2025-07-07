"""
Git 集成工具
提供代码版本控制、PR查询、分支管理等功能
"""

import os
import subprocess
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class GitOperations:
    """Git操作类"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        
    def run_git_command(self, command: List[str]) -> tuple[str, str, int]:
        """运行Git命令"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def get_repository_info(self) -> Dict[str, Any]:
        """获取仓库基本信息"""
        info = {}
        
        # 获取远程仓库URL
        stdout, stderr, code = self.run_git_command(['remote', 'get-url', 'origin'])
        if code == 0:
            info['remote_url'] = stdout.strip()
        
        # 获取当前分支
        stdout, stderr, code = self.run_git_command(['branch', '--show-current'])
        if code == 0:
            info['current_branch'] = stdout.strip()
        
        # 获取所有分支
        stdout, stderr, code = self.run_git_command(['branch', '-a'])
        if code == 0:
            branches = []
            for line in stdout.split('\n'):
                if line.strip():
                    branch = line.strip().replace('* ', '')
                    branches.append(branch)
            info['branches'] = branches
        
        # 获取最新提交
        stdout, stderr, code = self.run_git_command(['log', '-1', '--oneline'])
        if code == 0:
            info['latest_commit'] = stdout.strip()
        
        # 获取状态
        stdout, stderr, code = self.run_git_command(['status', '--porcelain'])
        if code == 0:
            info['status'] = stdout.strip()
            info['has_changes'] = bool(stdout.strip())
        
        return info
    
    def get_commit_history(self, days: int = 7, author: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取提交历史"""
        commits = []
        
        # 构建命令
        cmd = ['log', f'--since={days} days ago', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=iso']
        if author:
            cmd.extend(['--author', author])
        
        stdout, stderr, code = self.run_git_command(cmd)
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'email': parts[2],
                            'date': parts[3],
                            'message': '|'.join(parts[4:])
                        })
        
        return commits
    
    def get_file_changes(self, file_path: str, days: int = 30) -> List[Dict[str, Any]]:
        """获取文件变更历史"""
        changes = []
        
        cmd = ['log', f'--since={days} days ago', '--pretty=format:%H|%an|%ad|%s', '--date=iso', '--', file_path]
        stdout, stderr, code = self.run_git_command(cmd)
        
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        changes.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': '|'.join(parts[3:])
                        })
        
        return changes
    
    def get_branch_comparison(self, branch1: str, branch2: str) -> Dict[str, Any]:
        """比较两个分支"""
        comparison = {
            'commits_ahead': [],
            'commits_behind': [],
            'files_changed': []
        }
        
        # 获取branch1领先branch2的提交
        stdout, stderr, code = self.run_git_command(['log', f'{branch2}..{branch1}', '--oneline'])
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    comparison['commits_ahead'].append(line.strip())
        
        # 获取branch1落后branch2的提交
        stdout, stderr, code = self.run_git_command(['log', f'{branch1}..{branch2}', '--oneline'])
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    comparison['commits_behind'].append(line.strip())
        
        # 获取文件差异
        stdout, stderr, code = self.run_git_command(['diff', '--name-only', f'{branch1}..{branch2}'])
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    comparison['files_changed'].append(line.strip())
        
        return comparison
    
    def get_contributors(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取贡献者统计"""
        contributors = {}
        
        cmd = ['shortlog', '-sn', f'--since={days} days ago']
        stdout, stderr, code = self.run_git_command(cmd)
        
        if code == 0:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        count = int(parts[0])
                        name = parts[1]
                        contributors[name] = count
        
        return [{'name': name, 'commits': count} for name, count in contributors.items()]

def get_repository_info(repo_path: str = ".") -> str:
    """获取仓库信息"""
    try:
        git_ops = GitOperations(repo_path)
        info = git_ops.get_repository_info()
        
        result = f"📁 Git 仓库信息\n"
        result += f"{'='*50}\n\n"
        
        if 'remote_url' in info:
            result += f"🔗 远程仓库: {info['remote_url']}\n"
        
        if 'current_branch' in info:
            result += f"🌿 当前分支: {info['current_branch']}\n"
        
        if 'latest_commit' in info:
            result += f"📝 最新提交: {info['latest_commit']}\n"
        
        if 'has_changes' in info:
            status = "有未提交的更改" if info['has_changes'] else "工作区干净"
            result += f"📊 状态: {status}\n"
        
        if 'branches' in info:
            result += f"\n🌿 所有分支:\n"
            for branch in info['branches']:
                result += f"  • {branch}\n"
        
        return result
        
    except Exception as e:
        return f"❌ 获取仓库信息时出错: {e}"

def get_commit_history(repo_path: str = ".", days: int = 7, author: Optional[str] = None) -> str:
    """获取提交历史"""
    try:
        git_ops = GitOperations(repo_path)
        commits = git_ops.get_commit_history(days, author)
        
        result = f"📜 提交历史 (最近 {days} 天)\n"
        result += f"{'='*50}\n\n"
        
        if not commits:
            result += "没有找到提交记录\n"
            return result
        
        # 按日期分组
        commits_by_date = {}
        for commit in commits:
            date = commit['date'][:10]  # 只取日期部分
            if date not in commits_by_date:
                commits_by_date[date] = []
            commits_by_date[date].append(commit)
        
        # 显示提交记录
        for date in sorted(commits_by_date.keys(), reverse=True):
            result += f"📅 {date}\n"
            for commit in commits_by_date[date]:
                result += f"  • {commit['hash'][:8]} - {commit['author']}: {commit['message']}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ 获取提交历史时出错: {e}"

def get_file_changes(file_path: str, days: int = 30) -> str:
    """获取文件变更历史"""
    try:
        git_ops = GitOperations(os.path.dirname(file_path))
        changes = git_ops.get_file_changes(file_path, days)
        
        result = f"📄 文件变更历史 (最近 {days} 天)\n"
        result += f"{'='*50}\n\n"
        result += f"📄 文件: {file_path}\n\n"
        
        if not changes:
            result += "没有找到变更记录\n"
            return result
        
        for change in changes:
            result += f"📝 {change['hash'][:8]} - {change['author']}\n"
            result += f"   时间: {change['date']}\n"
            result += f"   提交: {change['message']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ 获取文件变更历史时出错: {e}"

def compare_branches(branch1: str, branch2: str, repo_path: str = ".") -> str:
    """比较分支"""
    try:
        git_ops = GitOperations(repo_path)
        comparison = git_ops.get_branch_comparison(branch1, branch2)
        
        result = f"🔄 分支比较: {branch1} vs {branch2}\n"
        result += f"{'='*50}\n\n"
        
        # 领先的提交
        if comparison['commits_ahead']:
            result += f"📈 {branch1} 领先 {branch2} 的提交:\n"
            for commit in comparison['commits_ahead']:
                result += f"  • {commit}\n"
            result += "\n"
        
        # 落后的提交
        if comparison['commits_behind']:
            result += f"📉 {branch1} 落后 {branch2} 的提交:\n"
            for commit in comparison['commits_behind']:
                result += f"  • {commit}\n"
            result += "\n"
        
        # 文件变更
        if comparison['files_changed']:
            result += f"📁 有差异的文件:\n"
            for file in comparison['files_changed']:
                result += f"  • {file}\n"
        
        if not any(comparison.values()):
            result += "两个分支没有差异\n"
        
        return result
        
    except Exception as e:
        return f"❌ 比较分支时出错: {e}"

def get_contributors_stats(repo_path: str = ".", days: int = 30) -> str:
    """获取贡献者统计"""
    try:
        git_ops = GitOperations(repo_path)
        contributors = git_ops.get_contributors(days)
        
        result = f"👥 贡献者统计 (最近 {days} 天)\n"
        result += f"{'='*50}\n\n"
        
        if not contributors:
            result += "没有找到贡献者记录\n"
            return result
        
        # 按提交数排序
        contributors.sort(key=lambda x: x['commits'], reverse=True)
        
        total_commits = sum(c['commits'] for c in contributors)
        result += f"📊 总提交数: {total_commits}\n\n"
        
        for i, contributor in enumerate(contributors, 1):
            percentage = (contributor['commits'] / total_commits) * 100
            result += f"{i}. {contributor['name']}: {contributor['commits']} 提交 ({percentage:.1f}%)\n"
        
        return result
        
    except Exception as e:
        return f"❌ 获取贡献者统计时出错: {e}"

def search_commits(query: str, repo_path: str = ".", days: int = 90) -> str:
    """搜索提交信息"""
    try:
        git_ops = GitOperations(repo_path)
        
        # 搜索提交信息
        cmd = ['log', f'--since={days} days ago', '--pretty=format:%H|%an|%ad|%s', '--date=iso', '--grep', query]
        stdout, stderr, code = git_ops.run_git_command(cmd)
        
        result = f"🔍 提交搜索结果\n"
        result += f"{'='*50}\n\n"
        result += f"🔍 搜索关键词: {query}\n"
        result += f"📅 时间范围: 最近 {days} 天\n\n"
        
        if code == 0 and stdout.strip():
            commits = []
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': '|'.join(parts[3:])
                        })
            
            if commits:
                result += f"📝 找到 {len(commits)} 个相关提交:\n\n"
                for commit in commits:
                    result += f"• {commit['hash'][:8]} - {commit['author']}\n"
                    result += f"  时间: {commit['date']}\n"
                    result += f"  信息: {commit['message']}\n\n"
            else:
                result += "没有找到相关提交\n"
        else:
            result += "没有找到相关提交\n"
        
        return result
        
    except Exception as e:
        return f"❌ 搜索提交时出错: {e}" 