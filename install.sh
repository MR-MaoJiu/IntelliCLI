#!/bin/bash
# IntelliCLI 快速安装脚本 (Unix/Linux/macOS)

set -e

echo "🚀 IntelliCLI 快速安装脚本"
echo "=========================="

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.8 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Python 版本过低: $PYTHON_VERSION (需要 >= $REQUIRED_VERSION)"
    exit 1
fi

echo "✅ Python 版本检查通过: $PYTHON_VERSION"

# 检查是否在项目目录中
if [ ! -f "pyproject.toml" ] || [ ! -d "intellicli" ]; then
    echo "❌ 请在 IntelliCLI 项目根目录中运行此脚本"
    exit 1
fi

echo "📁 当前目录: $(pwd)"

# 询问安装模式
echo ""
echo "请选择安装模式:"
echo "1) 正常安装 - 全局安装 IntelliCLI"
echo "2) 开发模式 - 可编辑安装，适合开发者"
echo "3) 退出"

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🔧 开始正常安装..."
        python3 -m pip install --upgrade pip
        python3 -m pip install .
        ;;
    2)
        echo "🔧 开始开发模式安装..."
        python3 -m pip install --upgrade pip
        python3 -m pip install -e .[dev]
        ;;
    3)
        echo "👋 安装已取消"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

# 验证安装
echo ""
echo "🧪 验证安装..."

if command -v intellicli &> /dev/null; then
    echo "✅ IntelliCLI 安装成功！"
    echo ""
    echo "🎉 现在您可以在任意位置运行以下命令:"
    echo "   • intellicli session  - 启动交互式会话"
    echo "   • intellicli chat      - 单次对话"
    echo "   • intellicli models    - 查看可用模型"
    echo "   • intellicli config    - 查看配置"
    echo "   • icli                 - 简短别名"
    echo ""
    echo "💡 首次运行时会自动启动配置向导"
    echo ""
    echo "🚀 开始使用:"
    echo "   intellicli session"
else
    echo "❌ 安装验证失败，请检查错误信息"
    exit 1
fi 