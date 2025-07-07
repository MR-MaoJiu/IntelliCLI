#!/usr/bin/env python3
"""
IntelliCLI 安装脚本
支持全局安装和开发模式安装
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd: str, description: str = ""):
    """运行命令并处理错误"""
    print(f"🔧 {description}...")
    print(f"   执行: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   输出: {result.stdout.strip()}")
        print(f"   ✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} 失败")
        print(f"   错误: {e.stderr}")
        return False

def install_package(dev_mode: bool = False):
    """安装 IntelliCLI 包"""
    print("🚀 开始安装 IntelliCLI...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 8):
        print("❌ IntelliCLI 需要 Python 3.8 或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    
    print(f"✅ Python 版本检查通过: {sys.version}")
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 项目目录: {project_root}")
    
    # 升级 pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级 pip"):
        return False
    
    # 安装依赖
    if dev_mode:
        install_cmd = f"{sys.executable} -m pip install -e .[dev]"
        description = "开发模式安装 IntelliCLI"
    else:
        install_cmd = f"{sys.executable} -m pip install ."
        description = "安装 IntelliCLI"
    
    if not run_command(install_cmd, description):
        return False
    
    # 验证安装
    try:
        result = subprocess.run("intellicli --help", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ IntelliCLI 安装成功！")
            print()
            print("🎉 现在您可以在任意位置运行以下命令:")
            print("   • intellicli session  - 启动交互式会话")
            print("   • intellicli chat      - 单次对话")
            print("   • intellicli models    - 查看可用模型")
            print("   • intellicli config    - 查看配置")
            print("   • icli                 - 简短别名")
            print()
            print("💡 首次运行时会自动启动配置向导")
            return True
        else:
            print("❌ 安装验证失败")
            return False
    except Exception as e:
        print(f"❌ 安装验证出错: {e}")
        return False

def uninstall_package():
    """卸载 IntelliCLI 包"""
    print("🗑️ 开始卸载 IntelliCLI...")
    
    if run_command(f"{sys.executable} -m pip uninstall intellicli -y", "卸载 IntelliCLI"):
        print("✅ IntelliCLI 卸载成功！")
        return True
    else:
        print("❌ IntelliCLI 卸载失败")
        return False

def main():
    parser = argparse.ArgumentParser(description="IntelliCLI 安装脚本")
    parser.add_argument("action", choices=["install", "uninstall"], help="执行的操作")
    parser.add_argument("--dev", action="store_true", help="开发模式安装（可编辑安装）")
    
    args = parser.parse_args()
    
    if args.action == "install":
        success = install_package(dev_mode=args.dev)
    elif args.action == "uninstall":
        success = uninstall_package()
    else:
        print("❌ 无效的操作")
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 